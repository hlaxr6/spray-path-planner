#!/usr/bin/env python

import rospy
import json
from rrad_wash_cell.srv import Modification

class SegmentModificationsClient():

    def __init__(self):
        pass

    def handle_modifications_client(self, jsonMods):
        print "about to try the ROS service"
        rospy.wait_for_service('mod')
        try:
            print "got to modifications_client"
            modifications = rospy.ServiceProxy('mod', Modification)
            if jsonMods == "startup":
                response = modifications(jsonMods)
            else:
                print "got to rework modification"
                response = modifications(jsonMods)
                #response = modifications(json.dumps(jsonMods))
            newPath = self.getPathArray(response.Path)
            filepath = response.filename

            ROSImpingementArray = response.Impingement
            impingementData = self.putImpingementDataIntoSimpleArray(ROSImpingementArray)
            return newPath, filepath, impingementData
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def getPathArray(self, pathROSMessage):
        segmentArray = pathROSMessage.lineSegmentArray
        length = pathROSMessage.numberOfLines
        print "Length: ",length
        path = []
        for index in range(length):
            #print index, segmentArray[index].index
            path.append(segmentArray[index].index)
            path.append(segmentArray[index].midpointX)
            path.append(segmentArray[index].midpointY)
            path.append(segmentArray[index].midpointZ)
            path.append(segmentArray[index].nozzleRotationX)
            path.append(segmentArray[index].nozzleRotationY)
            path.append(segmentArray[index].nozzleRotationZ)
            path.append(segmentArray[index].pointToX)
            path.append(segmentArray[index].pointToY)
            path.append(segmentArray[index].pointToZ)
            path.append(segmentArray[index].length)
            path.append(segmentArray[index].pointX)
            path.append(segmentArray[index].pointY)
            path.append(segmentArray[index].pointZ)
            path.append(segmentArray[index].times)

        return path

    def putImpingementDataIntoSimpleArray(self, ROSImpingementArray):
        ROSImpingArray = ROSImpingementArray.ImpingementArray

        impingementArray = []
        for index in range(ROSImpingementArray.numberOfFacets):
            impingementArray.append(ROSImpingArray[index].impinge)
        return impingementArray
