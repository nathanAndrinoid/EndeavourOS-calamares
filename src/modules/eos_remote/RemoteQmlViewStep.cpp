/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: no
 *   SPDX-License-Identifier: CC0-1.0
 */

#include "RemoteQmlViewStep.h"

#include "GlobalStorage.h"
#include "JobQueue.h"
#include "utils/Logger.h"

CALAMARES_PLUGIN_FACTORY_DEFINITION( RemoteQmlViewStepFactory, registerPlugin< RemoteQmlViewStep >(); )

RemoteQmlViewStep::RemoteQmlViewStep( QObject* parent )
    : Calamares::QmlViewStep( parent )
    , m_config( new RemoteConfig( this ) )
{
}

QString
RemoteQmlViewStep::prettyName() const
{
    return tr( "Remote Access" );
}

bool
RemoteQmlViewStep::isNextEnabled() const
{
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
    m_config->writeConfig();
}

void
RemoteQmlViewStep::setConfigurationMap( const QVariantMap& configurationMap )
{
    Calamares::QmlViewStep::setConfigurationMap( configurationMap );
}
