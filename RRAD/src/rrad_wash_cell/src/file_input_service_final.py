#!/usr/bin/env python

import rospy
import stl
from stl import mesh
import Tkinter, tkFileDialog
import std_msgs
from rrad_wash_cell.srv import *
last_mesh = None
import os
HOME = os.getenv("HOME")

def get_filename(name):
    root = Tkinter.Tk()
    root.withdraw()
    #change filepath for ease if needed
    base = tkFileDialog.askopenfilename(initialdir =HOME+'/RRAD/src/rrad_wash_cell/src/Test_Parts/')
    if base[-3:] == "stl":
        STL = base
        OBJ = base.replace('stl','obj')
    elif base[-3:] == "obj":
        OBJ = base
        STL = base.replace('obj','stl')

    root.destroy()
    print"File Found"
    return Input_MeshResponse(STL,OBJ)

def create_mesh():
    rospy.init_node('input_mesh_server')
    s = rospy.Service('input_mesh', Input_Mesh, get_filename)
    rospy.spin()


if __name__ == "__main__":
    print "Input Server"
    create_mesh()

