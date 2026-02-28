/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: no
 *   SPDX-License-Identifier: CC0-1.0
 */

#include "RemoteConfig.h"

#include <QByteArray>
#include <QFile>
#include <QTextStream>

RemoteConfig::RemoteConfig( QObject* parent )
    : QObject( parent )
{
}

void
RemoteConfig::setEnableSshd( bool v )
{
    if ( m_enableSshd != v )
    {
        m_enableSshd = v;
        emit enableSshdChanged();
    }
}

void
RemoteConfig::setImportGithubKeys( bool v )
{
    if ( m_importGithubKeys != v )
    {
        m_importGithubKeys = v;
        emit importGithubKeysChanged();
    }
}

void
RemoteConfig::setGithubUsername( const QString& v )
{
    if ( m_githubUsername != v )
    {
        m_githubUsername = v;
        emit githubUsernameChanged();
    }
}

void
RemoteConfig::setEnableRdp( bool v )
{
    if ( m_enableRdp != v )
    {
        m_enableRdp = v;
        emit enableRdpChanged();
    }
}

void
RemoteConfig::setRdpPassword( const QString& v )
{
    if ( m_rdpPassword != v )
    {
        m_rdpPassword = v;
        emit rdpPasswordChanged();
    }
}

void
RemoteConfig::writeConfig() const
{
    const QString configPath = QStringLiteral( "/tmp/eos-installer-ssh.conf" );
    QFile file( configPath );
    if ( !file.open( QIODevice::WriteOnly | QIODevice::Text ) )
        return;

    const QString passwordB64 =
        QString::fromLatin1( m_rdpPassword.toUtf8().toBase64() );

    QTextStream out( &file );
    out << "ENABLE_SSHD=" << ( m_enableSshd ? "true" : "false" ) << "\n";
    out << "IMPORT_GITHUB_KEYS=" << ( m_importGithubKeys ? "true" : "false" ) << "\n";
    out << "GITHUB_USERNAME=" << m_githubUsername << "\n";
    out << "ENABLE_RDP=" << ( m_enableRdp ? "true" : "false" ) << "\n";
    out << "RDP_PASSWORD_B64=" << passwordB64 << "\n";
}
