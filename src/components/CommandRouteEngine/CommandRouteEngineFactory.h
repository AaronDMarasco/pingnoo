/*
 * Copyright (C) 2020 Adrian Carpenter
 *
 * This file is part of Pingnoo (https://github.com/nedrysoft/pingnoo)
 *
 * An open-source cross-platform traceroute analyser.
 *
 * Created by Adrian Carpenter on 22/01/2020.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef NEDRYSOFT_COMMANDROUTEENGINE_COMMANDROUTEENGINEFACTORY_H
#define NEDRYSOFT_COMMANDROUTEENGINE_COMMANDROUTEENGINEFACTORY_H

#include "ComponentSystem/IInterface.h"
#include "Core/IRouteEngineFactory.h"

#include <memory>

namespace Nedrysoft::CommandRouteEngine {
    class CommandRouteEngineFactoryData;

    class CommandRouteEngine;

    /**
     * @brief       The CommandRouteEngineFactory class provides a factory for the CommandRouteEngine class.
     */
    class CommandRouteEngineFactory :
            public Nedrysoft::Core::IRouteEngineFactory {

        private:
            Q_OBJECT

            Q_INTERFACES(Nedrysoft::Core::IRouteEngineFactory)

        public:
            /**
             * @brief       Constructs a new CommandRouteEngineFactory.
             */
            CommandRouteEngineFactory();

            /**
             * @brief       Destroys the CommandRouteEngineFactory.
             */
            ~CommandRouteEngineFactory();

        public:
            /**
             * @brief       Creates a route engine instance.
             *
             * @details     Creates and returns a route engine instance.  The instance is owned by the factory
             *              and is responsible for its life cycle.
             *
             * @returns     the route engine instance.
             */
            virtual auto createEngine() -> Nedrysoft::Core::IRouteEngine *;

            /**
             * @brief       Returns the descriptive name of the route engine.
             *
             * @brief       Returns the description of the route engine, used to display the name of the engine
             *              to the user.
             *
             * @returns     the descriptive name of the route engine.
             */
            virtual auto description() -> QString;

            /**
             * @brief       Priority of the route engine.  The priority is 0=lowest, 1=highest.  This allows
             *              the application to provide a default engine per platform.
             *
             * @returns     the priority.
             */
            virtual auto priority() -> double;

        private:
            /**
             * @brief       Saves the configuration to a JSON object.
             *
             * @returns     the JSON configuration.
             */
            virtual auto saveConfiguration() -> QJsonObject;

            /**
             * @brief       Loads the configuration.
             *
             * @param[in]   configuration the configuration as JSON object.
             *
             * @returns     true if loaded; otherwise false.
             */
            virtual auto loadConfiguration(QJsonObject configuration) -> bool;

        protected:
            std::shared_ptr<CommandRouteEngineFactoryData> d;
    };
}


#endif // NEDRYSOFT_COMMANDROUTEENGINE_COMMANDROUTEENGINEFACTORY_H
