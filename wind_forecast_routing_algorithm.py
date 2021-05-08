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

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsFeatureSink,
                       QgsProject,
                       QgsVectorLayer,
                       QgsField,
                       QgsFields,
                       QgsRectangle,
                       QgsFeature,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsInterval,
                       QgsPointXY,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterMeshLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterDateTime,
                       QgsProcessingParameterFeatureSink)

from weatherrouting import Routing, Polar, Grib
from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter

import processing
import math
import os
from datetime import datetime, timedelta
import dateutil

class in_sea_checker:
    
    def __init__(self,domain_extent=None):

        global_oceans_layer_file = os.path.join(os.path.dirname(__file__),"ne_10m_ocean.zip")
        if domain_extent:
            alg_params = {
                "INPUT": global_oceans_layer_file,
                "EXTENT": domain_extent,
                "CLIP": True,
                "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT
            }
            print (alg_params)
            output_clip = processing.run('native:extractbyextent', alg_params)
            QgsProject.instance().addMapLayer(output_clip['OUTPUT'])
            self.sea_layer = output_clip['OUTPUT']
        else:
            self.sea_layer = QgsVectorLayer(local_sea_layer_file, "sea", 'ogr')

        for feat in self.sea_layer.getFeatures():
            sea_feat = feat
            break
        self.sea_geom = sea_feat.geometry()

    def point_in_sea_xy(self,y,x):
        return self.in_sea(QgsPointXY(x,y))

    def path_in_sea_xy(self,y1,x1,y2,x2):
        return self.in_sea(QgsGeometry.fromPolylineXY([QgsPointXY(x1,y1),QgsPointXY(x2,y2)]))
        
    def in_sea(self,p):
        #start_t = datetime.now()
        res = self.sea_geom.contains(p)
        #delay = datetime.now() - start_t
        #print ("in_sea sample delay:", delay.total_seconds())
        return res
        #return True


def heading(y,x):
    a = math.degrees(math.atan2(y,x))
    if a<0:
        a = 360 + a
    return (a + 360) % 360

def reduce360 (alfa):
	if math.isnan (alfa):
		return 0.0
		
	n=int(alfa*0.5/math.pi)
	n=math.copysign(n,1)
	if alfa>2.0*math.pi:
		alfa=alfa-n*2.0*math.pi
	if alfa<0:
		alfa=(n+1)*2.0*math.pi+alfa
	if alfa>2.0*math.pi or alfa<0:
		return 0.0
	return alfa

class grib_sampler(Grib):
    """ 
    Grib class is an abstract class that should be implement for providing grib data to routers
    """
    def __init__(self, gribLayer, wind_idx, destinationCrs=None):
        self.grib = gribLayer
        self.start_time = self.grib.dataProvider().temporalCapabilities().timeExtent().begin().toPyDateTime()
        self.end_time = self.grib.dataProvider().temporalCapabilities().timeExtent().end().toPyDateTime()
        if not destinationCrs:
            destinationCrs = QgsCoordinateReferenceSystem(4326)
        transform = QgsCoordinateTransform(self.grib.crs(), destinationCrs, QgsProject.instance().transformContext())
        self.grib.updateTriangularMesh(transform)
        self.wind_idx = wind_idx

    def getWindAt(self, t, lat, lon):
        """ Returns (twd, tws) for the given point (lat, lon) at time t """
        if t >= self.start_time and t<=self.end_time: 
            delta = t - self.start_time #self.grib.dataProvider().temporalCapabilities().referenceTime().toPyDateTime()
            interval = QgsInterval(delta.total_seconds())
            lon_lat = QgsPointXY(lon, lat)
            interval = self.grib.datasetIndexAtRelativeTime (interval, self.wind_idx) 
            wind_value = self.grib.datasetValue(interval, lon_lat)
            twd = math.radians(heading(wind_value.y(), wind_value.x()))
            #twd = math.degrees(reduce360(math.atan2( wind_value.y(),wind_value.x())+math.pi))
            tws = wind_value.scalar()#*1.943844
            return (twd,tws)
        else:
            print ("OUT_OF_RANGE")
            return None

class windForecastRoutingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_WAYPOINTS = 'OUTPUT_WAYPOINTS'
    OUTPUT_ROUTE = 'OUTPUT_ROUTE'
    GRIB = 'GRIB'
    WIND_DATASET_INDEX = 'WIND_DATASET_INDEX'
    START_POINT = 'START_POINT'
    END_POINT = 'END_POINT'
    POLAR = 'POLAR'
    START_TIME = 'START_TIME'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        #http://jieter.github.io/orc-data/site/
        self.polars_dir = os.path.join(os.path.dirname(__file__),"polar_files")
        self.polars = {}
        for polar_file in os.listdir(self.polars_dir):
            polar_name, ext = os.path.splitext(polar_file)
            if ext == '.pol':
                self.polars[polar_name] = polar_file
        self.polar_names = list(self.polars.keys())
        self.polar_names.sort()

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(QgsProcessingParameterMeshLayer(self.GRIB, self.tr('Grib layer')))
        self.addParameter(QgsProcessingParameterNumber(self.WIND_DATASET_INDEX, self.tr('Wind Grib Dataset index')))
        self.addParameter(QgsProcessingParameterEnum(self.POLAR, 'Polar (Courtesy of seapilot.com)', options=self.polar_names, defaultValue=None, allowMultiple=False))
        self.addParameter(QgsProcessingParameterPoint(self.START_POINT, self.tr('Start point')))
        self.addParameter(QgsProcessingParameterPoint(self.END_POINT, self.tr('End point')))
        self.addParameter(QgsProcessingParameterDateTime(self.START_TIME, self.tr('Time of departure')))
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_WAYPOINTS,
                self.tr('Waypoints Output layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_ROUTE,
                self.tr('Route Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        grib_layerfile = self.parameterAsFile(parameters, self.GRIB, context)
        grib_layer = self.parameterAsLayer(parameters, self.GRIB, context)
        wind_ds = self.parameterAsInt(parameters, self.WIND_DATASET_INDEX, context)
        polar_filename = self.polar_names[self.parameterAsEnum(parameters, self.POLAR, context)]
        polar = Polar(os.path.join(self.polars_dir,self.polars[polar_filename]))
        start = self.parameterAsDateTime(parameters, self.START_TIME, context)
        start_point = self.parameterAsPoint(parameters, self.START_POINT, context, crs=grib_layer.crs())
        end_point = self.parameterAsPoint(parameters, self.END_POINT, context, crs=grib_layer.crs())

        print ("grib_layerfile", grib_layerfile)
        print ("grib_layer", grib_layer)
        print ("wind_ds", wind_ds)
        print ("polar", polar)

        track = ((start_point.y(), start_point.x()), (end_point.y(), end_point.x()))
        geo_context = QgsRectangle(start_point.x(),start_point.y(), end_point.x(),end_point.y())
        track_dist = QgsPointXY(start_point.x(),start_point.y()).sqrDist(end_point.x(), end_point.y())
        geo_context.grow( (track_dist/2 ) if track_dist < 1 else 0.5 ) #limit grow to 0.5 degree
        checkValidity = in_sea_checker(geo_context)
        grib_reader = grib_sampler(grib_layer,wind_ds)

        #test
        #print ("TESTGRIB",grib_reader.getWindAt(datetime.strptime("02/02/21 18:00", "%d/%m/%y %H:%M"),39.31064,5.06086))

        print ("track", track)

        route_process =  Routing(LinearBestIsoRouter, polar, track, grib_reader, start.toPyDateTime(), lineValidity = checkValidity.path_in_sea_xy,)
        step = 1
        execution = "ok"
        while not route_process.end:
            if feedback.isCanceled():
                break
            try:
                res = route_process.step()
                step += 1
                feedback.pushInfo("step %d: %s" % (step, str(res.time)))
                if feedback.isCanceled():
                    return {"result":"terminated by user"}
                if res.time > grib_reader.end_time:
                    execution = "terminated: out of grib temporal scope"
            except Exception as e:
                feedback.pushInfo("Error: %s" % e.message)

        if res.path:
            waypfields = QgsFields()
            waypfields.append(QgsField("wayp_id", QVariant.Int))
            waypfields.append(QgsField("timestamp", QVariant.String,len=25))
            waypfields.append(QgsField("time", QVariant.DateTime)) 
            waypfields.append(QgsField("twd", QVariant.Double,len=10,prec=3)) 
            waypfields.append(QgsField("tws", QVariant.Double,len=10,prec=3)) 
            waypfields.append(QgsField("knots", QVariant.Double,len=10,prec=3)) 
            waypfields.append(QgsField("heading", QVariant.Double,len=10,prec=3)) 
            routefields = QgsFields()
            routefields.append(QgsField("start_tracking", QVariant.String,len=25))
            routefields.append(QgsField("end_tracking", QVariant.String,len=25))

            (sink_waypoints, dest_waypoints_id) = self.parameterAsSink(parameters, self.OUTPUT_WAYPOINTS,
                    context, waypfields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem(4326))
            (sink_route, dest_route_id) = self.parameterAsSink(parameters, self.OUTPUT_ROUTE,
                    context, routefields, QgsWkbTypes.LineString, QgsCoordinateReferenceSystem(4326))

            # Compute the number of steps to display within the progress bar and
            # get features from source
            tr = []
            for wp in res.path:
                if len(wp) == 3:
                    tr.append((wp[0], wp[1], str(wp[2]), 0, 0, 0, 0))
                else:
                    tr.append((wp[0], wp[1], str(wp[4]), wp[5], wp[6], wp[7], wp[8]))
            if execution == "ok":
                tr.append((*track[-1], dateutil.parser.parse(tr[-1][2])+timedelta(hours=1), 0, 0, 0, 0))
            
            print (tr)
            route_polyline = []


            for order,wayp in enumerate(tr):
                # Stop the algorithm if cancel button has been clicked
                print (wayp[1],wayp[0],wayp[2])
                if feedback.isCanceled():
                    break
                print (wayp[2], type(wayp[2]))
                new_feat = QgsFeature(waypfields)
                new_feat.setAttribute('wayp_id', order)
                new_feat.setAttribute('timestamp', str(wayp[2])[:25]) #.isoformat(timespec='minutes')
                new_feat.setAttribute('time', str(wayp[2]))
                new_feat.setAttribute('twd', math.degrees(wayp[3]))
                new_feat.setAttribute('tws', wayp[4])
                new_feat.setAttribute('knots', wayp[5])
                new_feat.setAttribute('heading', wayp[6])
                waypoint = QgsPointXY(wayp[1],wayp[0])
                route_polyline.append(waypoint)
                new_geom = QgsGeometry.fromPointXY(waypoint)
                new_feat.setGeometry(new_geom)
                sink_waypoints.addFeature(new_feat, QgsFeatureSink.FastInsert)

            new_route_feat = QgsFeature(routefields)
            new_route_feat.setAttribute('start_tracking', tr[0][2][:25])
            new_route_feat.setAttribute('end_tracking', tr[-2][2][:25])
            new_route_feat.setGeometry(QgsGeometry.fromPolylineXY(route_polyline))
            sink_route.addFeature(new_route_feat, QgsFeatureSink.FastInsert)

            return {
                self.OUTPUT_WAYPOINTS: dest_waypoints_id,
                self.OUTPUT_ROUTE: dest_route_id,
                "result": execution
            }
        else:
            return {"result", "no_path"}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'windrouting'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'sail tools'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return windForecastRoutingAlgorithm()
