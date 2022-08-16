#!/usr/bin/env python2
import numpy as np
import stl
import os
from stl import mesh


def find_mins_maxs(_mesh):
    minx, miny, minz, maxx, maxy, maxz = 0,0,0,0,0,0
    for p in _mesh.points:
        # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[0],p[3],p[6], maxx)
            minx = min(p[0],p[3],p[6], minx)
            maxy = max(p[1],p[4],p[7], maxy)
            miny = min(p[1],p[4],p[7], miny)
            maxz = max(p[2],p[5],p[8], maxz)
            minz = min(p[2],p[5],p[8], minz)
    print( "Min/Max: ",minx, maxx, miny, maxy, minz, maxz)
#    return minx, maxx, miny, maxy, minz, maxz



def main(filename):

    orig_mesh = mesh.Mesh.from_file(filename)

    print filename

    print 'Number of Facets: ',len(orig_mesh)

    find_mins_maxs(orig_mesh)

def crawler():
    global level, Adaptive, bintype,destination

    #modify to gather data on all parts in the defined directory
    base_directory = '/home/steven/RRAD/src/rrad_wash_cell/src/Test_Parts/reduced/'

    partfiles = os.listdir(base_directory)
    #print partfiles

    for x in range(len(partfiles)):
        if "." in str(partfiles[x]):
            filename = base_directory+partfiles[x]
            main(filename)



if __name__ == "__main__":
    crawler()
