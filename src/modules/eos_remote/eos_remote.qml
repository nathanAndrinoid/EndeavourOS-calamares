/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: no
 *   SPDX-License-Identifier: CC0-1.0
 */

import io.calamares.core 1.0
import io.calamares.ui 1.0

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

// Use QtQuick.Controls.Page as root to avoid Kirigami.Page's Primitives.IconPropertiesGroup
// type-registry conflict that occurs when Kirigami is loaded from both the compiled Calamares
// binary and the system QML path simultaneously.
Page {
    // hardcoded color scheme for dark mode EndeavourOS calamares
    readonly property color unfilledFieldColor: "#3A3F45"
    readonly property color positiveFieldColor: "#4E5661"
    readonly property color negativeFieldColor: "#7F3F3F"

    readonly property color unfilledFieldOutlineColor: "#5C6370"
    readonly property color positiveFieldOutlineColor: "#7F9F7F"
    readonly property color negativeFieldOutlineColor: "#BF616A"

    readonly property color headerTextColor: "#ffffff"
    readonly property color commentsColor: "#ffffff"

    header: Label {
        horizontalAlignment: Qt.AlignHCenter
        height: 50
        color: headerTextColor
        font.weight: Font.Medium
        font.pointSize: 14
        text: qsTr("Configure remote access (optional)")
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

    ColumnLayout {
        id: _formLayout
        spacing: Kirigami.Units.largeSpacing

        // ── SSH ──────────────────────────────────────────────────────────
        Column {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            CheckBox {
                id: _sshdCheck
                text: qsTr("Enable SSH server (sshd)")
                checked: config.enableSshd
                onCheckedChanged: config.setEnableSshd(checked)
            }

            Label {
                width: 550
                text: qsTr("Allows logging in to this machine over the network via SSH.")
                font.weight: Font.Thin
                font.pointSize: 9
                color: commentsColor
                wrapMode: Text.WordWrap
            }
        }

        // ── GitHub SSH keys ──────────────────────────────────────────────
        Column {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            CheckBox {
                id: _githubKeysCheck
                text: qsTr("Import SSH public keys from GitHub")
                checked: config.importGithubKeys
                onCheckedChanged: config.setImportGithubKeys(checked)
            }

            Label {
                width: 550
                text: qsTr("Your public keys from github.com/<username>.keys will be added to ~/.ssh/authorized_keys on first login.")
                font.weight: Font.Thin
                font.pointSize: 9
                color: commentsColor
                wrapMode: Text.WordWrap
            }

            Column {
                visible: _githubKeysCheck.checked
                width: 550
                spacing: Kirigami.Units.smallSpacing

                Label {
                    width: 550
                    text: qsTr("GitHub username")
                }

                TextField {
                    id: _githubField
                    width: 550
                    placeholderText: qsTr("your-github-username")
                    text: config.githubUsername
                    onTextChanged: config.setGithubUsername(text)
                    inputMethodHints: Qt.ImhNoAutoUppercase

                    palette.base: _githubField.text.length
                        ? positiveFieldColor : unfilledFieldColor
                    palette.highlight: _githubField.text.length
                        ? positiveFieldOutlineColor : unfilledFieldOutlineColor
                }

                Label {
                    width: 550
                    text: qsTr("Only alphanumeric characters and hyphens are allowed (GitHub username rules).")
                    font.weight: Font.Thin
                    font.pointSize: 9
                    color: commentsColor
                    wrapMode: Text.WordWrap
                }
            }
        }

        // ── KRDP / Remote Desktop ────────────────────────────────────────
        Column {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            CheckBox {
                id: _rdpCheck
                text: qsTr("Enable KDE Remote Desktop (KRDP)")
                checked: config.enableRdp
                onCheckedChanged: config.setEnableRdp(checked)
            }

            Label {
                width: 550
                text: qsTr("Enables the KDE Wayland RDP server so you can connect with any RDP client.")
                font.weight: Font.Thin
                font.pointSize: 9
                color: commentsColor
                wrapMode: Text.WordWrap
            }

            Column {
                visible: _rdpCheck.checked
                width: 550
                spacing: Kirigami.Units.smallSpacing

                Label {
                    width: 550
                    text: qsTr("RDP password")
                }

                Row {
                    width: 550
                    spacing: 20

                    TextField {
                        id: _rdpPassField
                        width: 550 / 2 - 10
                        placeholderText: qsTr("RDP password")
                        text: config.rdpPassword
                        onTextChanged: config.setRdpPassword(text)
                        echoMode: TextInput.Password
                        passwordMaskDelay: 300
                        inputMethodHints: Qt.ImhNoAutoUppercase

                        palette.base: _rdpPassField.text.length
                            ? positiveFieldColor : unfilledFieldColor
                        palette.highlight: _rdpPassField.text.length
                            ? positiveFieldOutlineColor : unfilledFieldOutlineColor
                    }

                    TextField {
                        id: _rdpPassConfirm
                        width: 550 / 2 - 10
                        placeholderText: qsTr("Repeat RDP password")
                        echoMode: TextInput.Password
                        passwordMaskDelay: 300
                        inputMethodHints: Qt.ImhNoAutoUppercase

                        palette.base: _rdpPassConfirm.text.length
                            ? ( _rdpPassField.text === _rdpPassConfirm.text
                                ? positiveFieldColor : negativeFieldColor )
                            : unfilledFieldColor
                        palette.highlight: _rdpPassConfirm.text.length
                            ? ( _rdpPassField.text === _rdpPassConfirm.text
                                ? positiveFieldOutlineColor : negativeFieldOutlineColor )
                            : unfilledFieldOutlineColor
                    }
                }

                Kirigami.InlineMessage {
                    width: 550
                    visible: _rdpPassConfirm.text.length > 0
                        && _rdpPassField.text !== _rdpPassConfirm.text
                    showCloseButton: false
                    type: Kirigami.MessageType.Error
                    text: qsTr("Passwords do not match.")
                }

                Label {
                    width: 550
                    text: qsTr("This password is used by RDP clients to authenticate. It is separate from your user account password.")
                    font.weight: Font.Thin
                    font.pointSize: 9
                    color: commentsColor
                    wrapMode: Text.WordWrap
                }
            }
        }

        // ── Info footer ──────────────────────────────────────────────────
        Label {
            width: 550
            text: qsTr("All remote access options are disabled by default. You can change these settings after installation.")
            font.weight: Font.Thin
            font.pointSize: 9
            color: commentsColor
            wrapMode: Text.WordWrap
        }
    }

    } // ScrollView
}
