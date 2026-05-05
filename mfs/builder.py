import os
import sys
from datetime import datetime

import jinja2
from yaml import safe_load

from mfs.common import Sourcer


class Builder:

	def get_jinja_template(self, template_file):
		with open(template_file, "r") as tempf:
			template = jinja2.Template(tempf.read())
			return template

	def parse_yaml_rule(self, package_section):
		if not isinstance(package_section, dict):
			raise TypeError("Found package section that is not in proper format.")

		name = list(package_section.keys())[0]
		body = list(package_section.values())[0]

		if not isinstance(body, str):
			raise ValueError(f"Expecting str: {body}")

		body_tmpl = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(body)
		body = body_tmpl.render(**self.arch)

		if name != "none":
			out = {
				"name": name,
				"sources": name,
				"unpack": self.sourcer.unpack(name),
				"build_steps": body
			}
		else:
			out = {
				"name": "none",
				"sources": "",
				"unpack": "",
				"build_steps": body
			}

		out.update(self.arch)
		return out

	def state_paths(self, package_name):
		state_dir = os.path.join(
			os.environ["CLFS"],
			".mfs-state",
			self.build,
			self.arch_name,
			self.steps
		)

		os.makedirs(state_dir, exist_ok=True)

		base = os.path.join(state_dir, package_name)

		return {
			"dir": state_dir,
			"running": base + ".running",
			"done": base + ".done",
			"failed": base + ".failed"
		}

	def write_state_file(self, path, package_name, status):
		with open(path, "w") as f:
			f.write(f"package={package_name}\n")
			f.write(f"profile={self.build}\n")
			f.write(f"arch={self.arch_name}\n")
			f.write(f"step={self.steps}\n")
			f.write(f"target={self.arch.get('target', '')}\n")
			f.write(f"status={status}\n")
			f.write(f"date={datetime.now().isoformat()}\n")

	def __init__(self, inpath, build, arch, steps):
		self.build = build
		self.arch_name = arch
		self.steps = steps
		self.loader = jinja2.FileSystemLoader(os.path.join(inpath, "templates"))
		self.jinja = jinja2.Environment(loader=self.loader)
		self.sourcer = Sourcer(self.build, os.path.join(os.environ["CLFS"]))

		with open(os.path.join(os.environ["CLFS"], "profiles", self.build, "arches", f"{arch}.yaml")) as myarch:
			self.arch = safe_load(myarch.read())["arch"]

		with open(os.path.join(inpath, "profiles", self.build, "steps", f"{steps}.yaml"), "r") as myf:
			for rule_name, rule in safe_load(myf.read()).items():
				if "defaults" in rule:
					defaults = rule["defaults"].copy()
				else:
					defaults = {}

				tmpl = self.jinja.get_template(defaults["template"])

				for package in rule["steps"]:
					rule = self.parse_yaml_rule(package)
					package_name = rule["name"]

					state = self.state_paths(package_name)

					if os.path.exists(state["done"]):
						print(f"Skipping {package_name}, already completed.")
						continue

					if os.path.exists(state["failed"]):
						os.remove(state["failed"])

					self.write_state_file(state["running"], package_name, "running")

					cmds = tmpl.render(rule)
					print(cmds)

					result = os.system(cmds)

					if result != 0:
						if os.path.exists(state["running"]):
							os.remove(state["running"])
						self.write_state_file(state["failed"], package_name, "failed")
						print(f"Error encountered -- exit code {result}")
						sys.exit(1)

					if os.path.exists(state["running"]):
						os.remove(state["running"])
					self.write_state_file(state["done"], package_name, "done")


# vim: ts=4 sw=4 noet
