/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: no
 *   SPDX-License-Identifier: CC0-1.0
 *
 *   Stores SSH/KRDP settings collected during the show phase and writes
 *   /tmp/eos-installer-ssh.conf for ssh_setup_script.sh to consume.
 */

#ifndef EOS_REMOTE_CONFIG_H
#define EOS_REMOTE_CONFIG_H

#include <QObject>
#include <QString>

class RemoteConfig : public QObject
{
    Q_OBJECT

    Q_PROPERTY( bool enableSshd READ enableSshd WRITE setEnableSshd NOTIFY enableSshdChanged )
    Q_PROPERTY( bool importGithubKeys READ importGithubKeys WRITE setImportGithubKeys NOTIFY importGithubKeysChanged )
    Q_PROPERTY( QString githubUsername READ githubUsername WRITE setGithubUsername NOTIFY githubUsernameChanged )
    Q_PROPERTY( bool enableRdp READ enableRdp WRITE setEnableRdp NOTIFY enableRdpChanged )
    Q_PROPERTY( QString rdpPassword READ rdpPassword WRITE setRdpPassword NOTIFY rdpPasswordChanged )

public:
    explicit RemoteConfig( QObject* parent = nullptr );

    bool enableSshd() const { return m_enableSshd; }
    bool importGithubKeys() const { return m_importGithubKeys; }
    QString githubUsername() const { return m_githubUsername; }
    bool enableRdp() const { return m_enableRdp; }
    QString rdpPassword() const { return m_rdpPassword; }

    void setEnableSshd( bool v );
    void setImportGithubKeys( bool v );
    void setGithubUsername( const QString& v );
    void setEnableRdp( bool v );
    void setRdpPassword( const QString& v );

    /** Write /tmp/eos-installer-ssh.conf with current settings. */
    void writeConfig() const;

signals:
    void enableSshdChanged();
    void importGithubKeysChanged();
    void githubUsernameChanged();
    void enableRdpChanged();
    void rdpPasswordChanged();

private:
    bool m_enableSshd = false;
    bool m_importGithubKeys = false;
    QString m_githubUsername;
    bool m_enableRdp = false;
    QString m_rdpPassword;
};

#endif  // EOS_REMOTE_CONFIG_H
