#!/usr/bin/env python
import rospy
import sys
import numpy
import csv
from rrad_wash_cell.srv import *
from rrad_wash_cell.msg import LineSegmentArray, LineSegment,ImpingementArray,Impinge
import os
HOME = os.getenv("HOME")

original_path = []
master_path = []
master_subpath_list = []
subpath_dict = []
master_filename = ''

#main server that is called by the GODOT interface
def mod_server():
    rospy.init_node('Modification_Server')
    s = rospy.Service('mod',Modification, output)
    #print "Server is Busy."
    rospy.spin()

#manages process based on rework or new path
def output(data):
    global original_path, master_path, master_subpath_list, subpath_dict, master_filename
    print "started building modified path"
    if data.JSON == "startup":
        filename = input_mesh_client('startup')
        path, impingement = path_planner_client(filename)
        filename = filename.rsplit(".", 1)[0]
        filename = filename + '_new.stl'
        master_filename = filename
        master_path = path
        original_path = path
    #For Bradens Impingement
        #impingement = impingement_client(filename)

    else:
        path, impingement = replanner_client(master_filename)
        #impingement = impingement_client(filename)
        master_path = path
        
    combine_export(path)
    FinishedPath = path_to_msg(path)
    print 'done'

    return ModificationResponse(FinishedPath,master_filename,impingement)

#calls input service to get filename
def input_mesh_client(filename):
    print 'Get Input'
    rospy.wait_for_service('input_mesh')
    try:
        get_file = rospy.ServiceProxy('input_mesh',Input_Mesh)
        resp = get_file(filename)
        return resp.STL
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

#calls impingement service to get an accurate simulation
def impingement_client(filename):
    print 'Get Impingement'
    rospy.wait_for_service('impingement')
    try:
        get_impinge = rospy.ServiceProxy('impingement',Impingement)
        resp = get_impinge(filename)
        return resp.Impingement
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

#calls the rework planner for partial toolpaths
def replanner_client(filename):
    rospy.wait_for_service('subpath_builder')
    try:
        build = rospy.ServiceProxy('subpath_builder', Subpath_Builder)
        msgpath = path_to_msg(master_path)        
        resp = build(filename,msgpath)
        resppath = msg_to_path(resp.Path)
        impingement = resp.Impingement
        print len(resppath), 'path from rework planner'
        return resppath, impingement
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

#calls the main path planner 
def path_planner_client(filename):
    print 'Build Initial Path'
    rospy.wait_for_service('path_planner')
    try:
        planner = rospy.ServiceProxy('path_planner',Path_Planner)
        resp = planner(filename)
        resppath = msg_to_path(resp.Path)
        impingement = resp.Impingement
        return resppath, impingement
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

#converts path to ros message
def path_to_msg(path):
    #print len(path), 'initial path'
    #print path[0]

    segmentArray = LineSegmentArray()
    segmentArray.numberOfLines = len(path)-1
    for row in range(len(path)):
        segment = LineSegment()
        segment.index = path[row][0]
        segment.midpointX = path[row][1]
        segment.midpointY = path[row][2]
        segment.midpointZ = path[row][3]
        segment.nozzleRotationX = path[row][4]
        segment.nozzleRotationY = path[row][5]
        segment.nozzleRotationZ = path[row][6]
        segment.pointToX = path[row][7]
        segment.pointToY = path[row][8]
        segment.pointToZ = path[row][9]
        segment.length = path[row][10]
        segment.pointX = path[row][11]
        segment.pointY = path[row][12]
        segment.pointZ = path[row][13]
        segment.times = path[row][14]
        segmentArray.lineSegmentArray.append(segment)
   
    return segmentArray

#converts ros message to path
def msg_to_path(msg):

    path = []
    l = msg.numberOfLines
    print l, 'msg to path length'
    segmentArray = msg.lineSegmentArray
    for row in range(l):
        segment = []
        segment.append(segmentArray[row].index)
        segment.append(segmentArray[row].midpointX)
        segment.append(segmentArray[row].midpointY)
        segment.append(segmentArray[row].midpointZ)
        segment.append(segmentArray[row].nozzleRotationX)
        segment.append(segmentArray[row].nozzleRotationY)
        segment.append(segmentArray[row].nozzleRotationZ)
        segment.append(segmentArray[row].pointToX)
        segment.append(segmentArray[row].pointToY)
        segment.append(segmentArray[row].pointToZ)
        segment.append(segmentArray[row].length)
        segment.append(segmentArray[row].pointX)
        segment.append(segmentArray[row].pointY)
        segment.append(segmentArray[row].pointZ)
        segment.append(segmentArray[row].times)
        path.append(segment)
    #print path[-10:]
    
    return path

#exports path for debugging if necessary
def combine_export(_path):
    p = len(_path)
    print p, 'export path'
    #print _path[-10:]
    excomb = [[[] for i in range(14)] for j in range((p+1))]
    header = ['Index','MidpointX','MidpointY','MidpointZ','NozzleX','NozzleY','NozzleZ','PointToX','PointToY','PointToZ','Length','PointX','PointY','PointZ']
    h = len(header)

    for x in range(0,h):
        excomb[0][x] = header[x]

    for x in range(0,p):
        k = x + 1
        excomb[k][0] = _path[x][0]
        excomb[k][1] = _path[x][1]
        excomb[k][2] = _path[x][2]
        excomb[k][3] = _path[x][3]
        excomb[k][4] = _path[x][4]
        excomb[k][5] = _path[x][5]
        excomb[k][6] = _path[x][6]
        excomb[k][7] = _path[x][7]
        excomb[k][8] = _path[x][8]
        excomb[k][9] = _path[x][9]
        excomb[k][10] = _path[x][10]
        excomb[k][11] = _path[x][11]
        excomb[k][12] = _path[x][12]
        excomb[k][13] = _path[x][13]
        
    
    with open(HOME+'/RRAD/src/rrad_wash_cell/src/Viz.csv', 'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(excomb)

if __name__ == "__main__":
    print 'path storage server'
    mod_server()
