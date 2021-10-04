# -*- coding: utf-8 -*-

"""
/***************************************************************************
 windForecastRouting
                                 A QGIS plugin
 sailing routing by wind forecast
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-30
        copyright            : (C) 2021 by enrico ferreguti
        email                : enricofer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'enrico ferreguti'
__date__ = '2021-03-30'
__copyright__ = '(C) 2021 by enrico ferreguti'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from .wind_forecast_routing_launch import windForecastLaunchAlgorithm

class windForecastLaunchNoOutputAlgorithm(windForecastLaunchAlgorithm):

    def initAlgorithm(self, config):
        config["nooutput"] = True
        super(windForecastLaunchNoOutputAlgorithm, self).initAlgorithm(config=config)

    def name(self):
        return 'windroutinglaunchnooutput'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return 'windrouting launch without output'

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Sail tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'sailtools'

    def createInstance(self):
        return windForecastLaunchNoOutputAlgorithm()