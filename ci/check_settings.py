#! /usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 EndeavourOS Contributors
# SPDX-License-Identifier: BSD-2-Clause
#
usage = """
Validates a Calamares settings.conf file by checking that all referenced
modules and config files actually exist.

Usage:
    check_settings.py <settings.conf> <modules_src_dir> <configs_data_dir>
        [--skip-modules "mod1 mod2 ..."]

Checks:
  - Every module: value in instances: has a directory in <modules_src_dir>/<module>/
  - Every config: value in instances: exists as a file in <configs_data_dir>/<config>
  - Every module referenced in sequence.show and sequence.exec (stripping @id
    suffixes) has a directory in <modules_src_dir>/<module>/
  - Modules referenced in settings.conf that appear in SKIP_MODULES are flagged
    as errors (they will not be installed even if source exists)

Exits with value 0 on success, otherwise:
    1 on missing dependencies
    2 on invalid command-line arguments
    3 on missing files or directories
    4 if files have invalid YAML syntax
    5 if validation errors are found (missing module or config)
"""

ERR_IMPORT, ERR_USAGE, ERR_FILE_NOT_FOUND, ERR_SYNTAX, ERR_INVALID = range(1, 6)

### DEPENDENCIES
#
#
try:
    from yaml import safe_load, YAMLError
except ImportError as e:
    print(e)
    print("Dependencies for this tool: py-yaml\n    pip install pyyaml")
    exit(ERR_IMPORT)

import os
import sys

### INPUT PARSING
#
#
if len(sys.argv) < 4:
    print(usage)
    exit(ERR_USAGE)

settings_file = sys.argv[1]
modules_src_dir = sys.argv[2]
configs_data_dir = sys.argv[3]

skip_modules = set()
i = 4
while i < len(sys.argv):
    if sys.argv[i] == "--skip-modules" and i + 1 < len(sys.argv):
        skip_modules = set(sys.argv[i + 1].split())
        i += 2
    else:
        print(usage)
        print(f"\nUnknown argument: {sys.argv[i]!r}")
        exit(ERR_USAGE)

### FILE/DIR EXISTENCE CHECKS
#
#
if not os.path.isfile(settings_file):
    print(f"Settings file '{settings_file}' does not exist.")
    exit(ERR_FILE_NOT_FOUND)

if not os.path.isdir(modules_src_dir):
    print(f"Modules source directory '{modules_src_dir}' does not exist.")
    exit(ERR_FILE_NOT_FOUND)

if not os.path.isdir(configs_data_dir):
    print(f"Configs data directory '{configs_data_dir}' does not exist.")
    exit(ERR_FILE_NOT_FOUND)

### YAML LOAD
#
#
with open(settings_file, "r") as f:
    try:
        settings = safe_load(f)
    except YAMLError as e:
        print(f"YAML error in '{settings_file}': {e}")
        exit(ERR_SYNTAX)

if not settings or not isinstance(settings, dict):
    print(f"Settings file '{settings_file}' is empty or not a mapping.")
    exit(ERR_SYNTAX)

### VALIDATION
#
#
errors = []


def module_exists(module):
    return os.path.isdir(os.path.join(modules_src_dir, module))


def config_exists(config):
    return os.path.isfile(os.path.join(configs_data_dir, config))


def strip_instance_id(ref):
    """Strip @id suffix: 'welcome@offline' -> 'welcome'."""
    return ref.split("@")[0] if "@" in ref else ref


def check_module(module, context):
    if not module_exists(module):
        errors.append(
            f"Module '{module}' ({context}) has no directory"
            f" in '{modules_src_dir}/{module}'"
        )
    elif module in skip_modules:
        errors.append(
            f"Module '{module}' ({context}) is in SKIP_MODULES"
            f" and will not be installed"
        )


# Check instances block
for entry in settings.get("instances", []) or []:
    if not isinstance(entry, dict):
        continue
    module = entry.get("module", "")
    config = entry.get("config", "")

    if module:
        check_module(module, "referenced in instances:")

    if config:
        if not config_exists(config):
            errors.append(
                f"Config '{config}' (referenced in instances:) does not exist"
                f" in '{configs_data_dir}/{config}'"
            )

# Check sequence block
for phase in settings.get("sequence", []) or []:
    if not isinstance(phase, dict):
        continue
    for phase_key in ("show", "exec"):
        refs = phase.get(phase_key, []) or []
        for ref in refs:
            module = strip_instance_id(ref)
            check_module(module, f"from '{ref}' in sequence.{phase_key}")

### REPORT
#
#
if errors:
    print(f"Validation of '{settings_file}' FAILED with {len(errors)} error(s):")
    for err in errors:
        print(f"  - {err}")
    exit(ERR_INVALID)
else:
    print(f"Validation of '{settings_file}' PASSED.")
    exit(0)
