#! /usr/bin/env python3
#
# SPDX-FileCopyrightText: no
# SPDX-License-Identifier: CC0-1.0
#
# Regression test: eos_pacman._copy_gnupg_dir() must copy a GnuPG directory
# without crashing on the POSIX socket files that gpg-agent leaves open
# (S.gpg-agent, S.gpg-agent.ssh, S.dirmngr, S.keyboxd, …).
#
# Background
# ----------
# shutil.copytree() raises [Errno 6] No such device or address when it
# tries to open a socket file as a regular file.  This caused eos_pacman to
# abort the installation at runtime with:
#
#   ERROR: Installation failed: "eos_pacman failed"
#   details: [('/etc/pacman.d/gnupg/S.gpg-agent', '…/gnupg/S.gpg-agent',
#              "[Errno 6] No such device or address: '…/S.gpg-agent'"), …]
#
# The fix is to pass an ignore callback to copytree that returns the names
# of any POSIX socket files found in the source directory.  This test verifies
# that _copy_gnupg_dir() (which wraps copytree with that callback) completes
# successfully and that regular files are copied while socket files are not.
#
# Usage
# -----
#   python3 test_gnupg_copy.py <path-to-eos_pacman-module-dir>
#
# Exit codes match configvalidator.py / check_settings.py convention:
#   0  PASS
#   1  import error (missing dependency)
#   2  bad arguments
#   3  path not found
#   5  test assertion failed

import os
import sys
import socket
import shutil
import tempfile
import types

ERR_IMPORT, ERR_USAGE, ERR_FILE_NOT_FOUND, ERR_SYNTAX, ERR_INVALID = range(1, 6)

### ARGUMENT VALIDATION
#
#
if len(sys.argv) != 2:
    print(__doc__)
    sys.exit(ERR_USAGE)

module_dir = sys.argv[1]
if not os.path.isdir(module_dir):
    print(f"Module directory not found: {module_dir!r}")
    sys.exit(ERR_FILE_NOT_FOUND)

### LIBCALAMARES STUB
#
# main.py imports libcalamares at module scope.  Provide a minimal stub so
# the module can be loaded without the Calamares runtime being present.
#
_libcal = types.ModuleType("libcalamares")
_libcal.globalstorage = types.SimpleNamespace(value=lambda k: None)
_libcal.utils = types.SimpleNamespace(
    host_env_process_output=lambda cmd, cb=None: None,
    debug=lambda msg: None,
)
_libcal.job = types.SimpleNamespace(configuration={})
sys.modules.setdefault("libcalamares", _libcal)

sys.path.insert(0, module_dir)
try:
    import main as eos_pacman
except ImportError as e:
    print(f"Cannot import eos_pacman main.py: {e}")
    sys.exit(ERR_IMPORT)

### INTERFACE CHECK
#
# If main.py does not expose _copy_gnupg_dir, the copy logic is not testable.
# That absence is itself a failure: naive inline copytree calls are the bug.
#
if not hasattr(eos_pacman, "_copy_gnupg_dir"):
    print(
        "FAIL: main.py does not define _copy_gnupg_dir(src, dst)\n"
        "      The gnupg copy is not independently testable; it likely uses\n"
        "      a bare shutil.copytree() call that will crash on socket files."
    )
    sys.exit(ERR_INVALID)

### HELPERS
#
#
def make_fake_gnupg(base):
    """Create a gnupg-like directory containing regular files AND socket files.

    Returns (gnupg_path, regular_names, open_socket_objects, socket_names).
    open_socket_objects must be closed by the caller after the test.
    """
    gnupg = os.path.join(base, "gnupg")
    os.makedirs(gnupg)

    regular = ["pubring.kbx", "trustdb.gpg", "gpg.conf"]
    for name in regular:
        with open(os.path.join(gnupg, name), "w") as f:
            f.write("placeholder")

    sock_candidates = [
        "S.gpg-agent",
        "S.gpg-agent.ssh",
        "S.gpg-agent.browser",
        "S.gpg-agent.extra",
        "S.keyboxd",
        "S.dirmngr",
    ]
    open_sockets = []
    created_sockets = []
    for name in sock_candidates:
        path = os.path.join(gnupg, name)
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.bind(path)
            open_sockets.append(s)
            created_sockets.append(name)
        except OSError:
            pass  # AF_UNIX unavailable in this environment; skip socket creation

    return gnupg, regular, open_sockets, created_sockets


### TEST
#
#
def test_copy_gnupg_skips_sockets():
    """_copy_gnupg_dir must succeed even when the source contains socket files.

    - All regular files must appear in the destination.
    - No socket file must appear in the destination.
    - No exception must be raised.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src_gnupg, regular_files, open_sockets, sock_names = make_fake_gnupg(tmp)
        dst_gnupg = os.path.join(tmp, "dst", "gnupg")

        try:
            eos_pacman._copy_gnupg_dir(src_gnupg, dst_gnupg)
        except Exception as e:
            print(f"FAIL: _copy_gnupg_dir raised an exception: {e}")
            return False
        finally:
            for s in open_sockets:
                s.close()

        for name in regular_files:
            if not os.path.isfile(os.path.join(dst_gnupg, name)):
                print(f"FAIL: regular file '{name}' was not copied to destination")
                return False

        for name in sock_names:
            dst_path = os.path.join(dst_gnupg, name)
            if os.path.exists(dst_path):
                print(f"FAIL: socket file '{name}' must not be copied to destination")
                return False

    return True


### ENTRY POINT
#
#
if __name__ == "__main__":
    ok = test_copy_gnupg_skips_sockets()
    if ok:
        print("PASS: _copy_gnupg_dir correctly skips POSIX socket files")
        sys.exit(0)
    else:
        sys.exit(ERR_INVALID)
