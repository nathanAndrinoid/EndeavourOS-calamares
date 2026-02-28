# SPDX-FileCopyrightText: no
# SPDX-License-Identifier: CC0-1.0
#
# eos_remote — show-phase view step that collects SSH / KRDP settings and
# writes /tmp/eos-installer-ssh.conf for ssh_setup_script.sh to consume.

if(NOT WITH_QML)
    calamares_skip_module( "eos_remote (QML is not supported in this build)" )
    return()
endif()

find_package(${qtname} ${QT_VERSION} CONFIG REQUIRED Core)

calamares_add_plugin(eos_remote
    TYPE viewmodule
    EXPORT_MACRO PLUGINDLLEXPORT_PRO
    SOURCES
        RemoteQmlViewStep.cpp
        RemoteConfig.cpp
    RESOURCES
        eos_remote.qrc
    LINK_PRIVATE_LIBRARIES
        ${qtname}::Core
    SHARED_LIB
)
