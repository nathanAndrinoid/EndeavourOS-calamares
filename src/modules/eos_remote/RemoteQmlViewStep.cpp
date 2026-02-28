/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: no
 *   SPDX-License-Identifier: CC0-1.0
 */

#include "RemoteQmlViewStep.h"

#include "GlobalStorage.h"
#include "JobQueue.h"
#include "utils/Logger.h"
#include "utils/String.h"

CALAMARES_PLUGIN_FACTORY_DEFINITION( RemoteQmlViewStepFactory, registerPlugin< RemoteQmlViewStep >(); )

RemoteQmlViewStep::RemoteQmlViewStep( QObject* parent )
    : Calamares::QmlViewStep( parent )
    , m_config( new RemoteConfig( this ) )
{
    // Re-evaluate the Next button whenever the GitHub import checkbox or
    // username field changes.  Calamares reads isNextEnabled() on demand but
    // only re-queries after a nextStatusChanged() emission.
    connect( m_config, &RemoteConfig::importGithubKeysChanged,
             this, [this]() { emit nextStatusChanged( isNextEnabled() ); } );
    connect( m_config, &RemoteConfig::githubUsernameChanged,
             this, [this]() { emit nextStatusChanged( isNextEnabled() ); } );
}

QString
RemoteQmlViewStep::prettyName() const
{
    return tr( "Remote" );
}

bool
RemoteQmlViewStep::isNextEnabled() const
{
    // Block "Next" when the user has ticked "Import GitHub SSH keys" but has
    // not yet typed a username.  An empty or whitespace-only username would
    // silently abort the import at script time; catching it here surfaces the
    // error before installation starts.
    if ( m_config->importGithubKeys() && m_config->githubUsername().trimmed().isEmpty() )
        return false;
    return true;
}

bool
RemoteQmlViewStep::isBackEnabled() const
{
    return true;
}

bool
RemoteQmlViewStep::isAtBeginning() const
{
    return true;
}

bool
RemoteQmlViewStep::isAtEnd() const
{
    return true;
}

Calamares::JobList
RemoteQmlViewStep::jobs() const
{
    return {};
}

void
RemoteQmlViewStep::onLeave()
{
    // If the user enabled RDP but left the password field blank, fall back to
    // the login password stored in GlobalStorage by the usersq module.
    // usersq runs before eos_remote in the show sequence, so the key is always
    // present here.  GlobalStorage stores it as Calamares::String::obscure()
    // (a bidirectional XOR); calling obscure() again recovers the plaintext.
    bool appliedFallback = false;
    if ( m_config->enableRdp() && m_config->rdpPassword().trimmed().isEmpty() )
    {
        auto* gs = Calamares::JobQueue::instance()->globalStorage();
        const QString obfuscated = gs->value( "password" ).toString();
        if ( !obfuscated.isEmpty() )
        {
            const QString loginPw = Calamares::String::obscure( obfuscated );
            if ( !loginPw.isEmpty() )
            {
                m_config->setRdpPassword( loginPw );
                appliedFallback = true;
            }
        }
    }
    m_config->writeConfig();
    // Clear the temporarily injected password so it does not linger in memory.
    if ( appliedFallback )
        m_config->setRdpPassword( QString() );
}

void
RemoteQmlViewStep::setConfigurationMap( const QVariantMap& configurationMap )
{
    Calamares::QmlViewStep::setConfigurationMap( configurationMap );
}
