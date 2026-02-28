/* === This file is part of Calamares - <https://calamares.io> ===
 *
 *   SPDX-FileCopyrightText: no
 *   SPDX-License-Identifier: CC0-1.0
 */

#ifndef EOS_REMOTE_VIEWSTEP_H
#define EOS_REMOTE_VIEWSTEP_H

#include "RemoteConfig.h"

#include "DllMacro.h"
#include "utils/PluginFactory.h"
#include "viewpages/QmlViewStep.h"

class PLUGINDLLEXPORT RemoteQmlViewStep : public Calamares::QmlViewStep
{
    Q_OBJECT

public:
    explicit RemoteQmlViewStep( QObject* parent = nullptr );

    QString prettyName() const override;

    bool isNextEnabled() const override;
    bool isBackEnabled() const override;

    bool isAtBeginning() const override;
    bool isAtEnd() const override;

    Calamares::JobList jobs() const override;

    void onLeave() override;

    void setConfigurationMap( const QVariantMap& configurationMap ) override;

    QObject* getConfig() override { return m_config; }

private:
    RemoteConfig* m_config;
};

CALAMARES_PLUGIN_FACTORY_DECLARATION( RemoteQmlViewStepFactory )

#endif  // EOS_REMOTE_VIEWSTEP_H
