from app import app
from modifications_client import SegmentModificationsClient
from TriangleListBuilder import TriangleListBuilder
from threading import Event
from flask import request
from ImpingementModel import ImpingementModel
import json


@app.route('/getPath', methods=['POST'])
def getPath():
    print "making modificationsClient"
    modificationsClient = SegmentModificationsClient()
    path, stlFilepath, impingementData= modificationsClient.handle_modifications_client("startup")

    print stlFilepath
    facets = getPartFacets(stlFilepath)

    startupDictionary = {}
    startupDictionary["path"] = path
    startupDictionary["partModel"] = facets
    startupDictionary["impingementData"] = impingementData
    return json.dumps(startupDictionary)
    
# @app.route('/getLength')
# def getLength():
#     pathListener = PathListener()
#     pathListener.run()
#     while pathListener.complete is False:
#         time.sleep(1)
#     return str(pathPoints.getLength())

@app.route('/pathModifications', methods=['POST'])
def pathModifications():
    print "sending modifications"
    json = request.get_json()

    modificationsClient = SegmentModificationsClient()
    newPath = modificationsClient.handle_modifications_client(json)
    return str(newPath)

@app.route('/sendSurfaceSelection', methods=['POST'])
def sendSurfaceSelection():
    dummy = request.data
    
    print 'data  ', dummy
    
#new Steven Edit
    print "making modificationsClient"
    modificationsClient = SegmentModificationsClient()
    path, stlFilepath, impingementData= modificationsClient.handle_modifications_client(dummy)

    facets = getPartFacets(stlFilepath)

    startupDictionary = {}
    startupDictionary["path"] = path
    startupDictionary["partModel"] = facets
    startupDictionary["impingementData"] = impingementData
    return json.dumps(startupDictionary)


#Original
#    modificationsClient = SegmentModificationsClient()
#    newPath = modificationsClient.handle_modifications_client(json)
#    return str(newPath)

def getPartFacets(filepath):
    print "getting model of part"

    builder = TriangleListBuilder(filepath)
    trianglesList = builder.getTriangles()

    return trianglesList

def getImpingementData(path, stlFilepath):
    print "getting impingement data"

    impingementModel = ImpingementModel()
    impingementData = impingementModel.createImpingementData(stlFilepath)
    
    return impingementData
