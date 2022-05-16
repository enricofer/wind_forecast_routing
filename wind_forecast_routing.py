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

from datetime import datetime,timedelta
import os
import sys
import inspect

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QAction, QMainWindow, QDockWidget, QMenu
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsDateTimeRange, 
    QgsTemporalNavigationObject,
    QgsApplication, 
    QgsProject, 
    QgsMeshLayer, 
    QgsMeshDatasetIndex, 
    QgsVectorLayer, 
    QgsLayerTreeLayer,
    QgsCoordinateReferenceSystem,
    QgsMeshDataProviderTemporalCapabilities,
    QgsReadWriteContext
)

from processing import execAlgorithmDialog, createAlgorithmDialog
from .wind_forecast_routing_provider import windForecastRoutingProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class windForecastRoutingPlugin(object):

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'riskmaps_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Wind Forecast Routing')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Wind Forecast Routing')
        self.toolbar.setObjectName(u'Wind Forecast Routing')
        self.provider = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AISS', message)
    
    def add_action(
        self,
        icon_path,
        text,
        callback = None,
        context = None,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)

        if callback:
            action.triggered.connect(callback)
        
        if context:
            action.setMenu(context)

        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = windForecastRoutingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        icon_path = os.path.join(self.plugin_dir,'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Wind Forecast Routing'),
            callback=self.launch_routing,
            parent=self.iface.mainWindow())

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def moveLegendNode(self,source,target):
        clone = source.clone()
        target.insertChildNode(0, clone)
        parent = source.parent()
        parent.removeChildNode(source)
        return clone
    
    def launch_routing(self):
        """Run method that loads and exec the processing algorithm dialog"""

        params = {} 
        results = execAlgorithmDialog('sailtools:windroutinglaunchnooutput', params)
        if results:
            print ("FINAL",results)

            #force project to wgs84
            #QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(4326))

            legendRoot = QgsProject.instance().layerTreeRoot()
            routinggroup = legendRoot.insertGroup(0, results["elab_name"])

            #force meshlayer to wgs84
            meshLayer = QgsMeshLayer(results['GRIB_OUTPUT'],"grib",'mdal')
            meshLayer.setCrs(QgsCoordinateReferenceSystem(4326))

            print("0",meshLayer.temporalProperties().isActive())

            dp = meshLayer.dataProvider()
            gprCount = dp.datasetGroupCount()
            for i in range(gprCount):
                meta = dp.datasetGroupMetadata(QgsMeshDatasetIndex(i, 0))
                isVector = meta.isVector()
                name = meta.name()
                if isVector:
                    break
            
            ctx =  QgsReadWriteContext()
            doc = QDomDocument("testdoc")
            elem_bak = doc.createElement("temporalProps")
            meshLayer.temporalProperties().writeXml(elem_bak, doc, ctx)

            print("1",meshLayer.temporalProperties().isActive())

            s = meshLayer.rendererSettings()
            s.setActiveVectorDatasetGroup(i) #QgsMeshDatasetIndex(i, 0)
            s.setActiveScalarDatasetGroup(i)
            meshLayer.setRendererSettings(s)
            QgsProject.instance().addMapLayer(meshLayer, False)
            meshLayer.loadNamedStyle(os.path.join(self.plugin_dir,"grib.qml"))
            routinggroup.insertChildNode(0, QgsLayerTreeLayer(meshLayer))

            contextlayer = QgsVectorLayer(results['OUTPUT_CONTEXT'], "context", "ogr")
            contextlayer.loadNamedStyle(os.path.join(self.plugin_dir,"context.qml"))
            QgsProject.instance().addMapLayer(contextlayer, False)
            routinggroup.insertChildNode(0, QgsLayerTreeLayer(contextlayer))

            routelayer = QgsVectorLayer(results['OUTPUT_ROUTE'], "route", "ogr")
            routelayer.loadNamedStyle(os.path.join(self.plugin_dir,"route.qml"))
            QgsProject.instance().addMapLayer(routelayer, False)
            routinggroup.insertChildNode(0, QgsLayerTreeLayer(routelayer))

            waypointslayer = QgsVectorLayer(results['OUTPUT_WAYPOINTS'], "waypoints", "ogr")
            waypointslayer.loadNamedStyle(os.path.join(self.plugin_dir,"waypoint.qml"))
            QgsProject.instance().addMapLayer(waypointslayer, False)
            routinggroup.insertChildNode(0, QgsLayerTreeLayer(waypointslayer))

            tc_start = results["route_start_time"] - timedelta(minutes=5)
            tc_end = results["route_end_time"] + timedelta(minutes=55)
            tc = self.iface.mapCanvas().temporalController()
            tc.setTemporalExtents(QgsDateTimeRange(tc_start,tc_end))
            tc.rewindToStart()
            if results["ANIMATION"]:
                tc.setNavigationMode(QgsTemporalNavigationObject.Animated)
                tc.playForward()
            else:
                tc.setNavigationMode(QgsTemporalNavigationObject.NavigationOff)

            meshLayer.temporalProperties().readXml(elem_bak, ctx)
            meshLayer.reload()

    
    def ex_launch_routing(self):
        """Run method that loads and exec the processing algorithm dialog"""
        params = {} 
        dialog = createAlgorithmDialog('sailtools:windroutinglaunch', params)
        dialog.show()
        dialog.exec_()
        results = dialog.results()
        dialog.close()
        print("results", results)
