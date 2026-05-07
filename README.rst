Vipnix From Scratch

===================

"Vipnix From Scratch" is a source-based bootstrap framework derived from FFS (Funtoo From Scratch), originally created by Daniel Robbins. VFScratch has been heavily modified to support a personalized MacaroniOS-based environment, integrating Macaroni EGO tooling, Macaroni ebuilds, and several improvements to cross-compilation, chroot isolation and bootstrap reliability.

This technology can be used to bootstrap a personalized MacaroniOS-compatible stage1 tarball, as well as "Alkaline" MUSL micro-containers, completely from source code, bootstrapping the system using a cross-compiler, which itself is bootstrapped from a local compiler, ensuring the final binary environment is a completely new and isolated "greenfield" environment.

Unlike the original FFS implementation, VFScratch includes fixes for architecture contamination during cross-toolchain generation, preventing host binaries and host libraries from leaking into the target rootfs during bootstrap stages. This allows clean cross-compilation for architectures such as i686, arm64 and riscv64, even when building from completely different host architectures.

VFScratch leverages the ``vchroot`` tool, a heavily modified and improved fork of Fchroot, designed to perform isolated builds of non-native architectures using QEMU when necessary, while also avoiding unnecessary emulation on native architectures such as arm64 hosts building arm64 targets.

Supported Build Artifacts

=========================

* ``gnu`` , Macaroni-compatible Stage1 Tarball, this is an initial Linux environment that can later be used to generate a full source-based system using MacaroniOS tooling and ebuild infrastructure. Supported build hosts currently include x86-64bit and arm64 systems, and supported targets include x86-64bit, i686, arm64 (aarch64) and riscv64.

* ``musl`` , Alkaline MUSL Micro-Container, this is a lightweight MUSL-based environment intended for custom runtimes and containerized environments. Supported targets currently include x86-64bit, arm64 and riscv64, with ongoing work for additional architectures.

Supported Build Systems

=======================

It is possible to run VFScratch on virtually any Linux or Linux-like system with a working C compiler and minimal dependencies.

The framework dynamically generates build scripts from YAML profiles and Jinja2 templates using Python 3. This design allows build steps to remain modular, readable and easy to customize without manually editing large shell scripts.

To build for non-native architectures, ``vchroot`` and its associated QEMU dependencies are required.

The Ideal Setup

===============

The recommended setup for VFScratch is a Linux system running LXD containers. This allows isolated builds, snapshotting, parallel bootstrap environments and safer experimentation while keeping the host system clean.

VFScratch can automatically inject local repository modifications into container builds, allowing rapid development and testing of bootstrap changes without manually copying files into containers.

Unlike the original FFS environment, the VFScratch workflow is designed around MacaroniOS tooling, EGO integration and Macaroni-compatible package management behavior.

LXD Setup

=========

This section documents the recommended LXD-based workflow.

First, configure LXD on your Linux system and ensure your containers have working network connectivity.

The following environment variables can be used to customize the behavior of the bootstrap launcher:

* ``LXD_LAUNCH_EXTRA_ARGS``

* ``LXD_VFS_SOURCE_IMAGE``

* ``LXD_INTERFACE``

Next, import a compatible Linux image and assign it an alias for use during bootstrap.

To launch a build:

::

  $ cd ~/VFScratch

  $ ci/lxd-baremetal/bin/vfs gnu arm-64bit

This will instantiate an isolated build container and execute the full bootstrap process inside the container environment.

Snapshots can optionally be used between build stages to accelerate development and debugging.
