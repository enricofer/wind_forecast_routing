"""
Model exported as python.
Name : inverted_clip
Group : mio_wind:routing
With QGIS : 32000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterExtent
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Inverted_clip(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('sourcelayer', 'source layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterExtent('extent', 'extent', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Inverted_clip', 'inverted_clip', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Create layer from extent
        alg_params = {
            'INPUT': parameters['extent'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CreateLayerFromExtent'] = processing.run('native:extenttolayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Assign projection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'INPUT': outputs['CreateLayerFromExtent']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AssignProjection'] = processing.run('native:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': parameters['sourcelayer'],
            'OVERLAY': outputs['AssignProjection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Difference
        alg_params = {
            'INPUT': outputs['AssignProjection']['OUTPUT'],
            'OVERLAY': outputs['Clip']['OUTPUT'],
            'OUTPUT': parameters['Inverted_clip']
        }
        outputs['Difference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['OUTPUT'] = outputs['Difference']['OUTPUT']
        return results

    def name(self):
        return 'inverted_clip'

    def displayName(self):
        return 'inverted_clip'

    def group(self):
        return 'Sail tools'

    def groupId(self):
        return 'sailtools'

    def createInstance(self):
        return Inverted_clip()
