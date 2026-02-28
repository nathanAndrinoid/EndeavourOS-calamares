#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: no
# SPDX-License-Identifier: CC0-1.0
#
# eos_pacman — Initialize the pacman keyring and mirrorlist, then copy both
# into the target system.  Selects the online or offline code path based on
# globalstorage["hasInternet"].
#
# Online path (mirrors shellprocess_initialize_pacman.conf):
#   1. Rank mirrors via /etc/calamares/scripts/update-mirrorlist
#   2. Install archlinux-keyring and endeavouros-keyring into the live env
#   3. Copy mirrorlist, endeavouros-mirrorlist, gnupg, and resolv.conf to target
#
# Offline path (mirrors shellprocess_initialize_pacman_offline.conf):
#   1. Run /etc/calamares/scripts/create-pacman-keyring
#   2. Run /etc/calamares/scripts/create-endeavouros-mirrorlist-offline
#   3. Copy the generated files to target

import os
import shutil
import stat

import libcalamares


def pretty_name():
    return "Initializing pacman"


def run():
    root = libcalamares.globalstorage.value("rootMountPoint")
    if not root:
        return "No rootMountPoint", "rootMountPoint is not set in globalstorage"

    is_online = bool(libcalamares.globalstorage.value("hasInternet"))

    try:
        if is_online:
            _run_online(root)
        else:
            _run_offline(root)
    except Exception as e:
        return "eos_pacman failed", str(e)

    return None


def _host(cmd):
    libcalamares.utils.host_env_process_output(cmd, None)


def _ignore_sockets(directory, names):
    """Return the subset of *names* that are POSIX socket files.

    shutil.copytree raises [Errno 6] No such device or address when it tries
    to open a socket file as a regular file.  gpg-agent leaves several such
    files (S.gpg-agent, S.dirmngr, S.keyboxd, …) inside /etc/pacman.d/gnupg
    while it is running.  Returning their names from this ignore callback
    causes copytree to skip them without raising an exception.
    """
    result = set()
    for name in names:
        try:
            if stat.S_ISSOCK(os.stat(os.path.join(directory, name)).st_mode):
                result.add(name)
        except OSError:
            pass
    return result


def _copy_gnupg_dir(src, dst):
    """Copy a GnuPG directory tree to *dst*, skipping POSIX socket files."""
    shutil.copytree(src, dst, ignore=_ignore_sockets, dirs_exist_ok=True)


def _run_online(root):
    _host(["bash", "/etc/calamares/scripts/update-mirrorlist"])
    _host(["pacman", "-Sy", "--noconfirm", "archlinux-keyring", "endeavouros-keyring"])

    pacman_d = os.path.join(root, "etc", "pacman.d")
    os.makedirs(pacman_d, exist_ok=True)
    for name in ("endeavouros-mirrorlist", "mirrorlist"):
        shutil.copy(os.path.join("/etc/pacman.d", name),
                    os.path.join(pacman_d, name))
    _copy_gnupg_dir("/etc/pacman.d/gnupg", os.path.join(pacman_d, "gnupg"))
    shutil.copy("/etc/resolv.conf", os.path.join(root, "etc", "resolv.conf"))


def _run_offline(root):
    for script in (
        "/etc/calamares/scripts/create-pacman-keyring",
        "/etc/calamares/scripts/create-endeavouros-mirrorlist-offline",
    ):
        os.chmod(script, 0o755)
        _host(["bash", script])

    pacman_d = os.path.join(root, "etc", "pacman.d")
    os.makedirs(pacman_d, exist_ok=True)
    shutil.copy("/etc/pacman.d/endeavouros-mirrorlist.offline-install",
                os.path.join(pacman_d, "endeavouros-mirrorlist"))
    shutil.copy("/etc/pacman.d/mirrorlist", os.path.join(pacman_d, "mirrorlist"))
    _copy_gnupg_dir("/etc/pacman.d/gnupg", os.path.join(pacman_d, "gnupg"))
