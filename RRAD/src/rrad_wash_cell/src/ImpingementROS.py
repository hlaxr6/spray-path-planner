#!/usr/bin/env python2

#Impingement Model
from __future__ import division
import rospy
import time
import csv as csv 
import numpy as np
from stl import mesh
from math import acos, degrees
from numpy import array, dot, arccos, clip
from numpy.linalg import norm
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from rrad_wash_cell.msg import ImpingementArray,Impinge
from rrad_wash_cell.srv import *
from stl import mesh
from matplotlib.pyplot import *
import os
HOME = os.getenv("HOME")

#main program called by ros node
def createImpingementData(meshFile):

    #Import part file
    part = mesh.Mesh.from_file(meshFile.filename)


    #Import/Modify path plan
    while True:
        csv_file_object = csv.reader(open(HOME+'/RRAD/src/rrad_wash_cell/src/PathPlan.csv','rb'))
        #csv_file_object = csv.reader(open('/home/local/GACL/bmj005/Desktop/ImpingementStarterStuff/PathPlanNew.csv','rb'))
        header = csv_file_object.next()
        index2 = index1+1
        data = []
        for row in csv_file_object:
            data.append(row)
        data = np.array(data)
        #print len(data)


    impinge_values = to_msg(dummy) #replace dummy with resulting list of ordered impingement values
                                   #1 dimension, no index. Index is place in list

    return ImpingementResponse(impinge_values)

#converts impingement to ros message
def to_msg(analysis):
    ImpingeArray = ImpingementArray()
    ImpingeArray.numberOfFacets = len(analysis)
    for x in range(len(analysis)):
        facet = Impinge()
        facet.index = x
        facet.impinge = analysis[x]
        ImpingeArray.ImpingementArray.append(facet)
    return ImpingeArray

#ros node
def create_impingement():
    rospy.init_node('impingement_server')
    s = rospy.Service('impingement', Impingement, createImpingementData)
    rospy.spin()


if __name__ == "__main__":
    print "Impingement Server"
    create_impingement()
