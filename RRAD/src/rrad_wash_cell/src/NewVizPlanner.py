#!/usr/bin/env python2
from __future__ import division
import rospy
import math
import numpy as np
import numpy.linalg
import stl
from scipy.spatial import ConvexHull
import csv
from mpl_toolkits import mplot3d
from matplotlib import pyplot as plt
from stl import mesh
from rrad_wash_cell.msg import LineSegmentArray, LineSegment,ImpingementArray,Impinge
from rrad_wash_cell.srv import *
from matplotlib.pyplot import *
from Tkinter import *
from scipy import stats
import os
HOME = os.getenv("HOME")


speed = 0

minx=0
miny=0
minz=0
maxx=0
maxy=0
maxz=0

newminx=0
newminy=0
newminz=0
newmaxx=0
newmaxy=0
newmaxz=0

bintype=0

sprayer_width,Rot_Deg,R_axis,Adaptive = 0,0,0,0
offset = 0
sprayer_distance = 0       
sprayer_adjust = 0

partname = ""

def run_gui(_mesh):
    #viz(_mesh)

    def callback():
        global sprayer_width,Rot_Deg,R_axis,Adaptive,offset,sprayer_distance, sprayer_adjust, bintype, speed, sprayer_angle
        R_axis = r_axis.get()
        Adaptive = adapt.get()
        bintype = binmethod.get()
        Rot_Deg = 0
        sprayer_distance = 11
        offset_percent = 10
        speed = 10
        sprayer_angle = 60

        if len(e1.get()) != 0:
            sprayer_distance = float(e1.get())
        if len(e2.get()) != 0:
            sprayer_angle = float(e2.get())
        if len(e3.get()) != 0:
            offset_percent = float(e3.get())
        if len(e4.get()) != 0:
            speed = float(e4.get())
        if len(e5.get()) != 0:
            Rot_Deg = float(e5.get())


        sprayer_adjust = sprayer_distance/2
        sprayer_width = round(2*(sprayer_distance*math.tan(sprayer_angle*math.pi/360))) #use 360 instead of 180 to cut angle in half
        offset = sprayer_width*(100-offset_percent)/100

        print sprayer_distance, sprayer_width, offset, sprayer_adjust

        master.destroy()

    master = Tk()
    master.geometry("+500+500")

    Label(master, text="Sprayer Distance").grid(row=0)
    Label(master, text="Sprayer Angle (1-179)").grid(row=1)
    Label(master, text="Overlap Percentage (0-99)").grid(row=2)
    Label(master, text="Base Velocity (unit/s)").grid(row=3)
    Label(master, text="Axis of Rotation").grid(row=4)
    Label(master, text="Degrees of Rotation (0-359)").grid(row=5)
    Label(master, text="Adapt Based On:").grid(row=6)
    Label(master, text="Adapt Using:").grid(row=7)

    r_axis = IntVar()
    adapt = IntVar()
    binmethod = IntVar()

    e1 = Entry(master)
    e2 = Entry(master)
    e3 = Entry(master)
    e4 = Entry(master)
    e5 = Entry(master)

    b1 = Radiobutton(master, text="X", variable=r_axis, value=1)
    b2 = Radiobutton(master, text="Y", variable=r_axis, value=2)
    b3 = Radiobutton(master, text="Z", variable=r_axis, value=3)
    b4 =Radiobutton(master, text="None", variable=r_axis, value=4)

    b5 = Radiobutton(master, text="Time", variable=adapt, value=1)
    b6 = Radiobutton(master, text="Distance", variable=adapt, value=2)
    b7 = Radiobutton(master, text="Both", variable=adapt, value=3)
    b8 = Radiobutton(master, text="Neither", variable=adapt, value=4)

    b11 = Radiobutton(master, text="Mean", variable=binmethod, value=1)
    b12 = Radiobutton(master, text="Mode", variable=binmethod, value=2)
    b13 = Radiobutton(master, text="Max", variable=binmethod, value=3)
    b14 = Radiobutton(master, text="Min", variable=binmethod, value=4)

    e1.grid(row=0, column=1, columnspan=2,sticky=E+W)
    e2.grid(row=1, column=1, columnspan=2,sticky=E+W)
    e3.grid(row=2, column=1, columnspan=2,sticky=E+W)
    e4.grid(row=3, column=1, columnspan=2,sticky=E+W)
    e5.grid(row=5, column=1, columnspan=2,sticky=E+W)
    b1.grid(row=4, column=1,sticky=W)
    b2.grid(row=4, column=2,sticky=W)
    b3.grid(row=4, column=3,sticky=W)
    b4.grid(row=4, column=4,sticky=W)
    b5.grid(row=6, column=1,sticky=W)
    b6.grid(row=6, column=2,sticky=W)
    b7.grid(row=6, column=3,sticky=W)
    b8.grid(row=6, column=4,sticky=W)
    b11.grid(row=7, column=1,sticky=W)
    b12.grid(row=7, column=2,sticky=W)
    b13.grid(row=7, column=3,sticky=W)
    b14.grid(row=7, column=4,sticky=W)

    button = Button(master,text='Send',command=callback)
    button.grid(row=8, column=1,sticky=E+W)


    b1.select()
    b7.select()
    b11.select()

    e1.insert(0,"11")
    e2.insert(0,"60")
    e3.insert(0,"10")
    e4.insert(0,"10")
    e5.insert(0,"0")

    mainloop()


def find_mins_maxs(_mesh):
    global minx, miny, minz, maxx, maxy, maxz, xyavg
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
    xyavg = np.mean([maxx,maxy])+sprayer_distance
    print( "Min/Max: ",minx, maxx, miny, maxy, minz, maxz,xyavg)
    return minx, maxx, miny, maxy, minz, maxz, xyavg




def viz_mesh(_mesh):  # add points back to function call for plotting orignal paths
    #l = len(points)
    #x = []
    #y = []
    #z = []
    #for k in range(0,(l)):
    #    x.append(points[k][0])
    #    y.append(points[k][1])
    #    z.append(points[k][2])

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = mplot3d.Axes3D(fig)

    #ax.scatter(x, y, z, c='r', marker='o')

    nmesh = mplot3d.art3d.Poly3DCollection(_mesh.vectors)
    nmesh.set_edgecolor('k')
    nmesh.set_facecolor('b')

    ax.add_collection3d(nmesh)
    
    scale = _mesh.points.flatten(-1)
    ax.auto_scale_xyz(scale, scale, scale)


    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()

    return

def viz_points(points):
    l = len(points)
 #   print points
    x = []
    y = []
    z = []
    for k in range(0,(l)):
        x.append(points[k][0])
        y.append(points[k][1])
        z.append(points[k][2])

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = mplot3d.Axes3D(fig)

    ax.scatter(x, y, z, c='r', marker='o')

    #ax.add_collection3d(mplot3d.art3d.Poly3DCollection(_mesh.vectors))
    #scale = _mesh.points.flatten(-1)
    #ax.auto_scale_xyz(scale, scale, scale)


    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()

    return

def viz_built_points(points):
    l = len(points)
    #print points
    x = []
    y = []
    z = []
    for k in range(0,(l)):
        x.append(points[k][0][0])
        y.append(points[k][0][1])
        z.append(points[k][0][2])

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = mplot3d.Axes3D(fig)

    ax.scatter(x, y, z, c='r', marker='o')

    #ax.add_collection3d(mplot3d.art3d.Poly3DCollection(_mesh.vectors))
    #scale = _mesh.points.flatten(-1)
    #ax.auto_scale_xyz(scale, scale, scale)


    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()

    return

def viz_bin_points(points):
    l = len(points)
 #   print points
    x = []
    y = []
    z = []
    for k in range(0,(l)):
        x.append(points[k][0][0][0])
        y.append(points[k][0][0][1])
        z.append(points[k][0][0][2])

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = mplot3d.Axes3D(fig)

    ax.scatter(x, y, c='r', marker='o')

    #ax.add_collection3d(mplot3d.art3d.Poly3DCollection(_mesh.vectors))
    #scale = _mesh.points.flatten(-1)
    #ax.auto_scale_xyz(scale, scale, scale)


    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()

    return



def rotate(_mesh):
    #check = raw_input("Enter axis to rotate about (N for no rotaion): ")
    #if R_axis != 'N' and R_axis != 'n':    
        #degrees = float(raw_input("Enter degrees of rotation: "))
    if R_axis == 1:
        _mesh.rotate([1, 0.0, 0.0], math.radians(Rot_Deg))
    if R_axis == 2:
        _mesh.rotate([0.0, 1, 0.0], math.radians(Rot_Deg))
    if R_axis == 3:
        _mesh.rotate([0.0, 0.0, 1], math.radians(Rot_Deg))
    if R_axis == 4:
        print( "No Rotation")

    return _mesh

def zero(_mesh, minx, maxx, miny, maxy, minz, maxz):
    difx = 0 - (minx + ((maxx-minx)/2))
    dify = 0 - (miny + ((maxy-miny)/2))
    difz = 0 - (minz + ((maxz-minz)/2))
    minx = minx + difx
    miny = miny + dify
    minz = minz + difz
    maxx = maxx + difx
    maxy = maxy + dify
    maxz = maxz + difz
    _mesh.x += difx
    _mesh.y += dify
    _mesh.z += difz

    return _mesh, minx, maxx, miny, maxy, minz, maxz

def fit_to_side(_points, _mesh,maxz,minz,sprayer_distance,offset,sprayer_width,orig_length):
    hsteps = int(math.ceil((maxz-minz)/offset))
    print 'slices',hsteps
    diff = abs(minz-(maxz-(hsteps)*offset))/2
    path = []
    times = []
    time_analysis = []
    distance_analysis = []
    switch = 1
    tot_dist = 0
    #viz_built_points(_points)
    for h in range(0,(hsteps+1)):
        zh = maxz - h*offset + diff
        binpoints = bin_slice(_points, zh, sprayer_width) 
        inter = slicer(_mesh,zh)
        newpath, polar = intpol(_mesh, zh, inter)
        print "newpath", len(newpath)
        modpath, d_analysis = dist_mod(newpath,binpoints,polar,h)
        dtime, t_analysis,slice_dist = timestamper(modpath,binpoints,polar)
        #print "dtime",len(dtime), len(t_analysis)
        time_analysis.append(t_analysis)
        distance_analysis.append(d_analysis)
        l = len(modpath)
        if switch > 0:     
            for k in range(0,l):
                path.append(modpath[k])
            for j in range(len(dtime)):
                times.append(dtime[j])
        if switch < 0:
            for k in range(l-1,-1,-1):
                path.append(modpath[k])
            for j in range(len(dtime)-1,-1,-1):
                times.append(dtime[j])

        times.append((sprayer_width/speed))
        tot_dist += float(offset + slice_dist)
        switch = switch * (-1)

    del times[-2:]

    ftimes = final_timestamper(times)

    #print "times", times,ftimes
    analysis = dummy_analysis(time_analysis,distance_analysis,orig_length,ftimes[-1],tot_dist)

    return path, ftimes, analysis

def dummy_analysis(time, dist, length,final_time,final_dist): 
    global partname
    print 'dummy analysis', len(time), len(dist), length
    total_dist_val = 0
    total_time_val = 0
    total_combined_val = 0
    covered = 0
    uncovered = 0
    bindata = None
    adaptdata = None
    if len(time) != len(dist):
        return None
    analysis = []
    analysisstats = []
    t = {}
    d = {}
    #print "time", len(time), time
    #print "dist", len(dist), dist

    for x in range(len(time)):
        for y in range(len(time[x])):
            if time[x][y][0] in t:
                val = max(t[time[x][y][0]], time[x][y][1])
                t[time[x][y][0]] = val
            else:
                t[time[x][y][0]] = time[x][y][1]

    for x in range(len(dist)):
        for y in range(len(dist[x])):
            if dist[x][y][0] in d:
                val = min(d[dist[x][y][0]], dist[x][y][1])
                d[dist[x][y][0]] = val
            else:
                d[dist[x][y][0]] = dist[x][y][1]

    #print len(d),len(t)

    for x in range(length):
        t.setdefault(x,0)
        d.setdefault(x,0)#sprayer_distance/2)

    #print len(d),len(t)    

    #print "Lengths",len(t),len(d),length
    for i in range(length):
        #mod = i % 2
     #   if i < 40:     #mod > 0:
     #       analysis.append([i,0])
     #   else:
        if d[i] == 0:
            analysis.append([i,float(d[i])])
            uncovered += 1
        #elif d[i] > 2*sprayer_distance:
        #    analysis.append([i,(0.00001*float(t[i]))])
        else:
            #print d[i]
            dist_val = (1-((float(d[i])/sprayer_distance)-1))
            #print dist_val,t[i]     
            combined_val = dist_val*float(t[i])
            analysis.append([i,combined_val])
            total_dist_val += dist_val
            total_time_val += float(t[i])
            total_combined_val += combined_val
            covered += 1

#insert switch case for title/info
    info = ""
    if bintype == 1:
            bindata = "Mean"
            info += "Mean"
    if bintype == 2:
            bindata = "Mode"
            info += "Mode"
    if bintype == 3:
            bindata = "Max"
            info += "Max"
    if bintype == 4:
            bindata = "Min"
            info += "Min"

    if Adaptive == 1:
            adaptdata = "Time"
            info += "Time"
    if Adaptive == 2:
            adaptdata = "Distance"
            info += "Distance"
    if Adaptive == 3:
            adaptdata = "Both"
            info += "Both"
    if Adaptive == 4:
            adaptdata = "Naive"
            info = ""

    dummyname = partname.rsplit( ".", 1)[0]
    name = dummyname.rsplit("/",1)[1]
    name += info
    name += str(sprayer_width)
    #print "analysis\n\n", analysis
    fullanalysis = []

    fullanalysis.append(["Part Name",name,"Slice Width", sprayer_width])
    fullanalysis.append([adaptdata,bindata])
    fullanalysis.append(["Index","Time Value", "Distance Value","Combined Value"])
    for i in range(length):
        if d[i] == 0:
            dist = d[i]
        else:
            dist = (1-((float(d[i])/sprayer_distance)-1))
        
        fullanalysis.append([analysis[i][0],t[i],dist,analysis[i][1]])

    newfilename = HOME+'/RRAD/src/rrad_wash_cell/src/Test_Data/'+ name +'Analysis.csv'


    with open(newfilename, 'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(fullanalysis)


    analysisstats.append(["Part Name",name,"Slice Width", sprayer_width])
    analysisstats.append([adaptdata,bindata])
    analysisstats.append(["Average Distance Value",float(total_dist_val/covered)])
    analysisstats.append(["Average Time Value",float(total_time_val/covered)])
    analysisstats.append(["Average Combined Value",float(total_combined_val/covered)])
    analysisstats.append(["Total Path Length",final_dist])
    analysisstats.append(["Total Path Time",final_time])
    analysisstats.append(["Percentage of Covered Facets",float(covered/length),covered,uncovered,length])


    newfilename = HOME+'/RRAD/src/rrad_wash_cell/src/Test_Data/'+ name +'AnalysisStats.csv'

    with open(newfilename, 'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(analysisstats)


    return analysis

def slicer(_mesh,zheight):
    facets = len(_mesh.normals)
    j=0
    intersect = np.zeros(facets)
    for x in range(0, facets):
        check = 0
        if _mesh.v0[x][stl.Dimension.Z] >= zheight:
            check += 1
        if _mesh.v1[x][stl.Dimension.Z] >= zheight:
            check += 2
        if _mesh.v2[x][stl.Dimension.Z] >= zheight:
            check += 4
        if check != 0 and check != 7:
            intersect[x] = check
            j += 1
    print 'intersecting facets', j
    return intersect

def bin_slice(_points, zheight, width):
    pnts = len(_points)
    print 'pnts',pnts
    interval = width/2.0 + width/20.0

    bincheck = []
    for x in range(0, pnts):
        if _points[x][0][2] >= (zheight - interval):
            if _points[x][0][2] <= (zheight + interval):
                bincheck.append([_points[x],x])   #consider modifying. _points already has index included

    print 'points in bin: ',len(bincheck)
    #viz_bin_points(bincheck)
    return bincheck


def update_point_minmax(x,y,z):
    global newminx, newmaxx, newminy, newmaxy, newminz, newmaxz

    if x > newmaxx:
        newmaxx = x
    if x < newminx:
        newminx = x
    if y > newmaxy:
        newmaxy = y
    if y < newminy:
        newminy = y
    if z > newmaxz:
        newmaxz = z
    if z< newminz:
        newminz = z
    return

def intpol(_mesh, zheight, intersect):
    facets = len(_mesh.normals)
    newsurf = []
    origsurf = []
    checksurf = []
    #print _mesh.normals

    for s in range(0, facets):
        if intersect[s] == 1: 
            p1 = _mesh.v0[s]
            p2 = _mesh.v1[s]
            p3 = _mesh.v0[s]
            p4 = _mesh.v2[s]
        if intersect[s] == 2: 
            p1 = _mesh.v1[s]
            p2 = _mesh.v0[s]
            p3 = _mesh.v1[s]
            p4 = _mesh.v2[s]
        if intersect[s] == 3: 
            p1 = _mesh.v0[s]
            p2 = _mesh.v2[s]
            p3 = _mesh.v1[s]
            p4 = _mesh.v2[s]
        if intersect[s] == 4: 
            p1 = _mesh.v2[s]
            p2 = _mesh.v0[s]
            p3 = _mesh.v2[s]
            p4 = _mesh.v1[s]
        if intersect[s] == 5: 
            p1 = _mesh.v0[s]
            p2 = _mesh.v1[s]
            p3 = _mesh.v2[s]
            p4 = _mesh.v1[s]
        if intersect[s] == 6: 
            p1 = _mesh.v1[s]
            p2 = _mesh.v0[s]
            p3 = _mesh.v2[s]
            p4 = _mesh.v0[s]
        if intersect[s] != 0 and intersect[s] != 7:
            rangex = p1[0] - p2[0]
            rangey = p1[1] - p2[1]
            rangez = p1[2] - p2[2]
            percent = (p1[2]-zheight)/rangez
            nx = p1[0] - rangex*percent
            ny = p1[1] - rangey*percent

            newx, newy, newz = sprayoffset(nx,ny,zheight,_mesh.normals[s], sprayer_distance)
            newp = (newx,newy,newz,_mesh.normals[s])
            origp = (nx,ny)
            newsurf.append(newp)
            origsurf.append(origp)
            update_point_minmax(newx,newy,newz)

            rangex = p3[0] - p4[0]
            rangey = p3[1] - p4[1]
            rangez = p3[2] - p4[2]
            percent = (p3[2]-zheight)/rangez
            nx = p3[0] - rangex*percent
            ny = p3[1] - rangey*percent
            
            newx, newy, newz = sprayoffset(nx,ny,zheight,_mesh.normals[s], sprayer_distance)
            newp = (newx,newy,newz,_mesh.normals[s])
            origp = (nx,ny)
            newsurf.append(newp)
            origsurf.append(origp)
            update_point_minmax(newx,newy,newz)

    #print "newsurf",newsurf

    newsurf, origsurf = smooth_corner(newsurf,origsurf, zheight)

    newsurf, origsurf = unique_points(newsurf,origsurf)

    sortsurf,sortorig, pol_cords = polar_sort(newsurf,origsurf)

    binsurf,binorig, pol_cord = create_bins(sortsurf,sortorig,pol_cords)

#    return newsurf
    if len(binsurf) != 0:
        binsurf.append(binsurf[0])
        pol_cord.append(pol_cord[0])

    #return binsurf[78:95], pol_cord[78:95]
    return binsurf, pol_cord

def create_bins(_surf,_orig,phi):
    l = len(phi)
    bin_size = 10

    add_surf = []
    add_orig = []

    for x in range(1,l):
        y = x-1
        a = np.asarray([_surf[x][0],_surf[x][1],_surf[x][2]])
        b = np.asarray([_surf[y][0],_surf[y][1],_surf[y][2]])
        v = a-b
        dist = np.linalg.norm(v)
        num_bins = int((math.floor(dist/bin_size))+1)

        if num_bins > 1:
            bin_length = dist/num_bins
            u_surf = unit_vector(v)

            for i in range(1,num_bins):
                dummy_surf = list(_surf[y])
                vec = bin_length*i

                dummy_surf[0] = _surf[y][0]+u_surf[0]*vec
                dummy_surf[1] = _surf[y][1]+u_surf[1]*vec
                dummy_surf[2] = _surf[y][2]+u_surf[2]*vec

                add_surf.append(dummy_surf)

            a1 = np.asarray([_orig[x][0],_orig[x][1]])
            b1 = np.asarray([_orig[y][0],_orig[y][1]])
            v1 = a1-b1
            dist1 = np.linalg.norm(v1)
            bin_length1 = dist1/num_bins
            u_orig = unit_vector([v1[0],v1[1],0])

            for i in range(1,num_bins):
                dummy_orig = list(_orig[y])
                vec = bin_length1*i

                dummy_orig[0] = _orig[y][0]+u_orig[0]*vec
                dummy_orig[1] = _orig[y][1]+u_orig[1]*vec

                add_orig.append(dummy_orig)

    for j in range(len(add_surf)):
        _surf.append(add_surf[j])

    for j in range(len(add_orig)):
        _orig.append(add_orig[j])

    _surf,_orig, pol_cord = polar_sort(_surf,_orig)

    return _surf, _orig, pol_cord

def bin_points_time(_points,_path, pol_cord):    
    matched_pnts = []

    if len(_path) == 0 or len(_points) == 0:
        return matched_pnts

    for x in range(1,len(pol_cord)):
        y = x-1
        p1 = (_path[x][0],_path[x][1])
        p2 = (_path[y][0],_path[y][1])
        bin_pnts = []
        #for i in range(len(_points)-1,-1,-1):
        #    r = (_points[i][0][0][0],_points[i][0][0][1])
        #    d = norm((_points[i][0][1][0],_points[i][0][1][1]))
        #    projected = RayIntersect2D(r, d, p1, p2)
        #    if len(projected) == 1:
        #        dummy, val = get_polar(projected[0][0],projected[0][1])
            #if len(projected) == 0:
            #    val = 100
            #if val >= float(pol_cord[y]) and val <= float(pol_cord[x]):
        #        dummy_impinge = impingement(_points[i][0][0],np.asarray(_path[y][3])+np.asarray(_path[x][3]))
        #        bin_pnts.append([_points[i][0],dummy_impinge])

        #Edge Case Scenarios
            #if y == 0 and val < float(pol_cord[y]) and val < 10 :
            #    dummy_impinge = impingement(_points[i][0][0],np.asarray(_path[y][3])+np.asarray(_path[x][3]))
            #    bin_pnts.append([_points[i][0],dummy_impinge])

            #if x == (len(pol_cord)-1) and val > float(pol_cord[x]) and val < 10:
            #    dummy_impinge = impingement(_points[i][0][0],np.asarray(_path[y][3])+np.asarray(_path[x][3]))
            #    bin_pnts.append([_points[i][0],dummy_impinge])


        for i in range(len(_points)-1,-1,-1):
            r = (_points[i][0][0][0],_points[i][0][0][1])
            d = norm((_path[x][3][0],_path[x][3][1]))
            projected = RayIntersect2D(r, d, p1, p2)
            if len(projected) == 1:
                dummy, val = get_polar(projected[0][0],projected[0][1])
            #if len(projected) == 0:
            #    val = 100
            #if val >= float(pol_cord[y]) and val <= float(pol_cord[x]):
                dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
                #if dist < xyavg:
                dummy_impinge = impingement(_points[i][0][1],np.asarray(_path[y][3])+np.asarray(_path[x][3]))
                if dummy_impinge > 0.001:
                    bin_pnts.append([_points[i][0],dummy_impinge])

        #Edge Case Scenarios
            #if y == 0 and val < float(pol_cord[y]) and val < 10 :
            #    dummy_impinge = impingement(_points[i][0][0],np.asarray(_path[y][3])+np.asarray(_path[x][3]))
             #   bin_pnts.append([_points[i][0],dummy_impinge])

            #if x == (len(pol_cord)-1) and val > float(pol_cord[x]) and val < 10:
            #    dummy_impinge = impingement(_points[i][0][0],np.asarray(_path[y][3])+np.asarray(_path[x][3]))
            #    bin_pnts.append([_points[i][0],dummy_impinge])


                #_points.remove(i)

        impinge = []
        refpnts = []
        for j in range(len(bin_pnts)):
            refpnts.append(bin_pnts[j][0][2])
            impinge.append(bin_pnts[j][1])
#########################
        #mean/mode/max/min
        if bintype == 1:
            if len(impinge)>0: matched_pnts.append([refpnts,np.mean(impinge),impinge])
        if bintype == 2:
            if len(impinge)>0: matched_pnts.append([refpnts,float(stats.mode(impinge)[0][0]),impinge])
        if bintype == 3:
            if len(impinge)>0: matched_pnts.append([refpnts,np.max(impinge),impinge])
        if bintype == 4:
            if len(impinge)>0: matched_pnts.append([refpnts,np.min(impinge),impinge])

        if len(impinge)==0: matched_pnts.append([refpnts,1,impinge])

    return matched_pnts

def bin_points_dist(bin_points,_path, pol_cord):    
    global foundpoints
    matched_pnts = []
    _points = bin_points
    if len(_path) == 0 or len(_points) == 0:
        return matched_pnts

#    print "points",_points
#    print "path", _path
#    print "pol_cord\n\n\n", pol_cord

#   [[intersect,dist,i,j,val],i]
    #print "polar cord\n",pol_cord

    for x in range(1,len(pol_cord)):
        y = x-1
        p1 = (_path[x][0],_path[x][1])
        p2 = (_path[y][0],_path[y][1])
        bin_pnts = []
        #for i in range(len(_points)-1,-1,-1):
        #    r = (_points[i][0][0][0],_points[i][0][0][1])
        #    d = norm((_points[i][0][1][0],_points[i][0][1][1]))
        #    projected = RayIntersect2D(r, d, p1, p2)
        #    if len(projected) == 1:
        #        dummy, val = get_polar(projected[0][0],projected[0][1])
            #if len(projected) == 0:
            #    val = 100
            #print 'val', val
            #print "testcord",val
            #if val >= float(pol_cord[y]) and val <= float(pol_cord[x]):
        #        dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
        #        bin_pnts.append([_points[i][0],dist])
        #        foundpoints += 1

        #Edge Case Scenarios
            #if y == 0 and val < float(pol_cord[y]) and val < 10:
            #    dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
            #    bin_pnts.append([_points[i][0],dist])
            #    foundpoints += 1

            #if x == (len(pol_cord)-1) and val > float(pol_cord[x]) and val < 10:
            #    dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
            #    bin_pnts.append([_points[i][0],dist])
            #    foundpoints += 1


        for i in range(len(_points)-1,-1,-1):
            r = (_points[i][0][0][0],_points[i][0][0][1])
            d = norm((_path[x][3][0],_path[x][3][1]))
            projected = RayIntersect2D(r, d, p1, p2)
            if len(projected) == 1:
                dummy, val = get_polar(projected[0][0],projected[0][1])
            #if len(projected) == 0:
            #    val = 100
            #print 'val', val
            #print "testcord",val
            #if val >= float(pol_cord[y]) and val <= float(pol_cord[x]):
                dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
                #if dist < xyavg:
                imptest = impingement(_points[i][0][1],_path[x][3])
                if imptest > 0.001:
                    bin_pnts.append([_points[i][0],dist])
                    foundpoints += 1

        #Edge Case Scenarios
            #if y == 0 and val < float(pol_cord[y]) and val < 10:
            #    dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
            #    bin_pnts.append([_points[i][0],dist])
            #    foundpoints += 1

            #if x == (len(pol_cord)-1) and val > float(pol_cord[x]) and val < 10:
            #    dist = point_to_line_dist(_points[i][0],[[_path[x][0],_path[x][1],_path[x][2]],[_path[y][0],_path[y][1],_path[y][2]]])
            #    bin_pnts.append([_points[i][0],dist])

                #_points.remove(i)

        distance = []
        refpnts = []
        #print "BinPnts\n",bin_pnts
        for j in range(len(bin_pnts)):
            refpnts.append(bin_pnts[j][0][2])
            distance.append(bin_pnts[j][1])
            #distance.append(sprayer_width)

############################
        #mean/mode/max/min
        #print "bintype ",bintype
######Max/Min are flipped here because the minimum distance is best, where as the maximum impingement value is best
        if bintype == 1:
            if len(distance)>0: 
                matched_pnts.append([refpnts,np.mean(distance),distance])
        if bintype == 2:
            if len(distance)>0: 
                matched_pnts.append([refpnts,float(stats.mode(distance)[0][0]),distance])
        if bintype == 3:
            if len(distance)>0: 
                matched_pnts.append([refpnts,np.min(distance),distance])    #used when max is selected
        if bintype == 4:
            if len(distance)>0: 
                matched_pnts.append([refpnts,np.max(distance),distance])    #used when min is selected
        #print "dist ",len(distance)
        if len(distance)==0: 
            matched_pnts.append([refpnts,sprayer_distance,distance])
            #print 'zero points ##################################'
#    print matched_pnts

    print 'points found so far: ',foundpoints
    return matched_pnts

def point_to_line_dist(_point, _line):
    #modified from blenders mathutils.geometry.intersect_point_line()
    #https://stackoverflow.com/questions/27161533/find-the-shortest-distance-between-a-point-and-line-segments-not-line
    """Calculate the distance between a point and a line segment.

    To calculate the closest distance to a line segment, we first need to check
    if the point projects onto the line segment.  If it does, then we calculate
    the orthogonal distance from the point to the line.
    If the point does not project to the line segment, we calculate the 
    distance to both endpoints and take the shortest distance.

    :param point: Numpy array of form [x,y], describing the point.
    :type point: numpy.core.multiarray.ndarray
    :param line: list of endpoint arrays of form [P1, P2]
    :type line: list of numpy.core.multiarray.ndarray
    :return: The minimum distance to a point.
    :rtype: float
    """
    point = np.asarray(_point[0])
    line = np.asarray(_line)
    #print 'test################',point,line
    # unit vector
    unit_line = line[1] - line[0]
    norm_unit_line = unit_line / np.linalg.norm(unit_line)

    # compute the perpendicular distance to the theoretical infinite line
    segment_dist = (
        np.linalg.norm(np.cross(line[1] - line[0], line[0] - point)) /
        np.linalg.norm(unit_line)
    )

    diff = ((norm_unit_line[0] * (point[0] - line[0][0])) + (norm_unit_line[1] * (point[1] - line[0][1])))

    x_seg = (norm_unit_line[0] * diff) + line[0][0]
    y_seg = (norm_unit_line[1] * diff) + line[0][1]

    endpoint_dist = min(np.linalg.norm(line[0] - point),np.linalg.norm(line[1] - point))

    # decide if the intersection point falls on the line segment
    lp1_x = line[0][0]  # line point 1 x
    lp1_y = line[0][1]  # line point 1 y
    lp2_x = line[1][0]  # line point 2 x
    lp2_y = line[1][1]  # line point 2 y
    is_betw_x = lp1_x <= x_seg <= lp2_x or lp2_x <= x_seg <= lp1_x
    is_betw_y = lp1_y <= y_seg <= lp2_y or lp2_y <= y_seg <= lp1_y
    if is_betw_x and is_betw_y:
        return segment_dist
    else:
        # if not, then return the minimum distance to the segment endpoints
        return endpoint_dist

def dist_mod(_path,_points,pol_cord,slicecheck):  #2 3
    l = len(_path)
    #print 'path',l,'points',len(_points),'pol_cord',len(pol_cord)
    modpath = []
    print 'new slice'
    for i in range(l):
        modp = list([_path[i][0],_path[i][1],_path[i][2],list(_path[i][3])])
        modpath.append(modp)
    #l = 0
    analysis = []
    if l == 0 or len(_points) == 0:
        return modpath, analysis

    lastval = -1
    newdistance = []

    
    _bins = bin_points_dist(_points,_path, pol_cord)
    #print "bins",_bins


#    print "\n\nlength ",len(_bins),l
#    print modpath
    #print "length ", l, len(_bins)
    for x in range(1,l):
        y = x - 1
        #distval = abs(_bins[y][1]/sprayer_distance)-1

        j = 0
        total_distval = 0
        for i in range(-1,2):
            z = y + i
            if z >= 0 and z < (l-1):
                #print z
                total_distval = total_distval + 1*(abs(_bins[z][1]/sprayer_distance)-1) #(3 - abs(i))
                j = j + 1 #3 - abs(i)
                #print 'j ', j
        distval = total_distval/j

#testing for direction of move
#        if y == 20 or y == 80:
#            distval = 0.5
        checkset = [4,5,6,7,8,9,10,11,12,13,14,15,16]

        if distval < 0: distval = 0
        if distval > 0.95: distval = 0.95
        if Adaptive == 2 or Adaptive == 3:
            if distval > lastval:
                unit_vec = unit_vector(np.asarray([_path[y][3][0],_path[y][3][1],_path[y][3][2]]))
                modpath[y][0] = _path[y][0]-(distval*sprayer_adjust*unit_vec[0])
                modpath[y][1] = _path[y][1]-(distval*sprayer_adjust*unit_vec[1])
                modpath[y][2] = _path[y][2]-(distval*sprayer_adjust*unit_vec[2])

            unit_vec = unit_vector(np.asarray([_path[x][3][0],_path[x][3][1],_path[x][3][2]]))
            modpath[x][0] = _path[x][0]-(distval*sprayer_adjust*unit_vec[0])
            modpath[x][1] = _path[x][1]-(distval*sprayer_adjust*unit_vec[1])
            modpath[x][2] = _path[x][2]-(distval*sprayer_adjust*unit_vec[2])

            newdist = [_bins[y][2][z]-sprayer_adjust*distval for z in range(len(_bins[y][2]))]

            
            #if slicecheck not in checkset:
            #    print "slice found", slicecheck
            #    newdist = [_bins[y][2][z]-_bins[y][2][z] for z in range(len(_bins[y][2]))]

            #newdist = [_bins[y][2][z] for z in range(len(_bins[y][2]))]
            #print "newdist",newdist,_bins[y][0]
            newdistance.append(newdist)

        if Adaptive == 1 or Adaptive ==4:
            newdist = [_bins[y][2][z] for z in range(len(_bins[y][2]))]
            #print "newdist",newdist,_bins[y][0]
            newdistance.append(newdist)

        lastval = distval

#    print _bins[:,0], '\n\n'
#    print newdistance
    #binzip = []
    #for i in range (len(newdistance)):
    #    binzip.append(list(_bins[i][0]))
    #analysis = list(zip(binzip,newdistance))


    if len(_points) != 0:    
        for i in range (len(newdistance)):
            zipmid = _bins[i][0]
            for j in range (len(zipmid)):
                analysis.append([zipmid[j],newdistance[i][j]])

    return modpath, analysis

def unique_points(newsurf, origsurf):
    #strips extra points
    j = len(newsurf)
    opt2 = np.ones(j)
    delpoints  = []
    s = 0
    skip = 0
    while sum(opt2) != 0: 
        if opt2[s] == 1:
            unit_length_s = math.sqrt(math.pow(newsurf[s][3][0],2)+math.pow(newsurf[s][3][1],2)+math.pow(newsurf[s][3][2],2))
            unit_vec_s = unit_vector([newsurf[s][3][0],newsurf[s][3][1],newsurf[s][3][2]])
        #    print unit_vec_s, "vec s"
            for t in range(s,j):
                if s != t and opt2[t] == 1 and abs(origsurf[s][0] - origsurf[t][0]) < .01 and abs(origsurf[s][1] - origsurf[t][1]) < .01:
                    opt2[t] = 0

##############replace with unit vector function

                    unit_vec_t = unit_vector([newsurf[t][3][0],newsurf[t][3][1], newsurf[t][3][2]])
                    norm_dif = abs(unit_vec_s[0]-unit_vec_t[0]) + abs(unit_vec_s[1]-unit_vec_t[1]) + abs(unit_vec_s[2]-unit_vec_t[2])
        #            print unit_vec_t, "vec t"
        #            print norm_dif, "normdif"
                    if norm_dif < .1:
        #                print "del"
                        delpoints.append(t)
        opt2[s] = 0
        s += 1

    delpoints.sort()
#    print delpoints
#    print len(newsurf)
    if len(delpoints) != 0:
        k = len(delpoints) - 1
        #print k
        for x in range(k,-1,-1):
            newsurf.pop(delpoints[x])
            origsurf.pop(delpoints[x])
#    print len(newsurf), "delsurfs"

    return newsurf, origsurf

def smooth_corner(newsurf, origsurf, zheight):
#Combines normals of points that share a location
    j = len(newsurf)
    opt = np.ones(j)
    newpoints  = []
    s = 0
    skip = 0
    while sum(opt) != 0: 
        if opt[s] == 1:
            for t in range(s,j):
                if s != t and opt[t] == 1 and abs(origsurf[s][0] - origsurf[t][0]) < .01 and abs(origsurf[s][1] - origsurf[t][1]) < .01:

                    nux = float(newsurf[s][3][0] + newsurf[t][3][0])
                    nuy = float(newsurf[s][3][1] + newsurf[t][3][1])
                    nuz = float(newsurf[s][3][2] + newsurf[t][3][2])
                    nun = np.array([nux,nuy,nuz])
                    newx, newy, newz = sprayoffset(origsurf[s][0],origsurf[s][1],zheight,nun, sprayer_distance)
                    newentry = (newx,newy,newz,nun,s,origsurf[s][0],origsurf[s][1])
                    opt[t] = 0
                    newpoints.append(newentry)
        opt[s] = 0
        s += 1

    newpoints = sorted(newpoints, key=lambda pos: newentry[4])
    k = len(newpoints) - 1

    for x in range(k,-1,-1):
        entry = (newpoints[x][0],newpoints[x][1],newpoints[x][2],newpoints[x][3])
        pos = newpoints[x][4] + 1
        newsurf.insert(pos,entry)
        ogentry = (newpoints[x][5],newpoints[x][6])
        origsurf.insert(pos,ogentry)

#    print len(newsurf), "len newsurf", len(origsurf)
#    newsurface = sorted(newsurf, key=lambda newp: newp[0])
#    print len(newsurface)
    return newsurf, origsurf


def polar_sort(_surf,_orig):

    k = len(_surf)

    sortval = []
    sortedpath = []
    sortedorig = []
    phi = []

#    print k, 'k'

    for x in range(0,k):
        dummy1, val1 = get_polar(_orig[x][0],_orig[x][1])
        dummy2, val2 = get_polar(_surf[x][0],_surf[x][1])
        #surface/offset based weighting
        #val = (val1+val2)/2
        #val = val1  #Naive surface based
        val = val2   #True positioning sorting
        sortval.append ((_surf[x],_orig[x],val))

    sortedval = sorted(sortval, key = lambda sortval: sortval[2])

    #    print sortval, 'sortval'
    #    print sortedval, 'sorted'
    for x in range(0,k):
        sortedpath.append(sortedval[x][0])
        sortedorig.append(sortedval[x][1])
        phi.append(sortedval[x][2])

    #print 'Polar Values################\n',phi
    
    return sortedpath,sortedorig,phi


def sprayoffset(x,y,z,norm, sprayer_distance):
    unit_vec = unit_vector(norm)
    newx = x + sprayer_distance*unit_vec[0]
    newy = y + sprayer_distance*unit_vec[1]
    newz = z + sprayer_distance*unit_vec[2]

    return newx, newy, newz


def point_to_line(_path):
    k = len(_path)
    lines = []
    ind = 0
    previous = []
    for x in range(0,k):
        if x < (k-1):
            y = x + 1
            length  = math.sqrt(pow((_path[x][0] - _path[y][0]),2)+pow((_path[x][1] - _path[y][1]),2)+pow((_path[x][2] - _path[y][2]),2))
            pointer = (_path[y][0],_path[y][1],_path[y][2])
            midpoint = ((_path[x][0]+0.5*(_path[y][0]-_path[x][0])),(_path[x][1]+0.5*(_path[y][1]-_path[x][1])),(_path[x][2]+0.5*(_path[y][2]-_path[x][2])))
            #print "Nozzle ", x
            checkpoints = [3,357]
            if x in checkpoints:
                pr = True
                #print "Nozzle ", x
            else:
                pr = False
            rotation = get_nozzle_rotation(_path[x],_path[y],pr,previous)
            previous = rotation
            entry = (ind,midpoint,rotation,pointer,length)
            lines.append(entry)
            ind += 1

    return lines

def get_nozzle_rotation(p1,p2,pr,previous):
    #if pr == True:
        #print "Nozzle\n",p1,p2
    vect = np.array([(p1[3][0]+p2[3][0]),(p1[3][1]+p2[3][1]),(p1[3][2]+p2[3][2])])
    #if pr == True:
        #print "vect ",vect
    norm = np.array([(p2[0]-p1[0]),(p2[1]-p1[1]),(p2[2]-p1[2])])
    #if pr == True:
        #print "norm ", norm
    magnorm = math.sqrt(math.pow(norm[0],2)+math.pow(norm[1],2)+math.pow(norm[2],2))
    #if pr == True:
        #print "magnorm ", magnorm
    if magnorm == 0.0:
        print 'non fatal error'
        return previous
    cros = (np.cross(vect,norm))/magnorm
    #if pr == True:
        #print "cros ", cros
    project = (np.cross(norm,cros))/magnorm  #projection of the nozzle onto a plane perpendicular to the line
    #if pr == True:
        #print "project ",project    

    dist  = math.sqrt(pow(project[0],2)+pow(project[1],2)+pow(project[2],2))
    #if pr == True:
        #print "dist ", dist
    if dist == 0.0:
        print 'non fatal error'
        return previous
    newproject = (sprayer_distance*project[0]/dist,sprayer_distance*project[1]/dist,sprayer_distance*project[2]/dist)
    #if pr == True:
        #print "new project  ",newproject
    point_to = ((p1[0]-newproject[0]),(p1[1]-newproject[1]),(p1[2]-newproject[2]))
    #dista  = math.sqrt(pow(newpoint_to[0],2)+pow(newpoint_to[1],2)+pow(newpoint_to[2],2))
    #print dista
    return point_to

def combine_export(_line,_path, times):
    p = len(_path)
    l = len(_line)
    t = len(times)
   # print( p,'p',l,'l',t,'t')
    excomb = [[[] for i in range(15)] for j in range((p+1))]
    header = ['Index','MidpointX','MidpointY','MidpointZ','NozzleX','NozzleY','NozzleZ','PointToX','PointToY','PointToZ','Length','PointX','PointY','PointZ','TimeStamp']
    h = len(header)
    
    for x in range(0,h):
        excomb[0][x] = header[x]

    for x in range(0,l):
        k = x + 1
        excomb[k][0] = _line[x][0]
        excomb[k][1] = _line[x][1][0]
        excomb[k][2] = _line[x][1][1]
        excomb[k][3] = _line[x][1][2]
        excomb[k][4] = _line[x][2][0]
        excomb[k][5] = _line[x][2][1]
        excomb[k][6] = _line[x][2][2]
        excomb[k][7] = _line[x][3][0]
        excomb[k][8] = _line[x][3][1]
        excomb[k][9] = _line[x][3][2]
        excomb[k][10] = _line[x][4]

    for x in range(0,p):
        k = x + 1
        excomb[k][11] = _path[x][0]
        excomb[k][12] = _path[x][1]
        excomb[k][13] = _path[x][2]
        excomb[k][14] = times[x]
        
    for x in range(1,11):
        excomb[p][x] = 'NULL'
    excomb[p][0] = p - 1

    with open(HOME+'/RRAD/src/rrad_wash_cell/src/PathPlan.csv', 'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(excomb)

    return excomb

def export_path_only(_line,_path, times):
    p = len(_path)
    l = len(_line)
    t = len(times)
   # print( p,'p',l,'l',t,'t')
    excomb = [[[] for i in range(8)] for j in range((p+1))]
    header = ['Index','NormalX','NormalY','NormalZ','PointX','PointY','PointZ','TimeStamp']
    h = len(header)
    
    for x in range(0,h):
        excomb[0][x] = header[x]

    for x in range(0,l):
        k = x + 1
        excomb[k][0] = _line[x][0]

        #Direction Vector
        VX=_line[x][2][0]-_path[x][0]
        VY=_line[x][2][1]-_path[x][1]
        VZ=_line[x][2][2]-_path[x][2]

        #Vector Magnitude
        M=(VX**2+VY**2+VZ**2)**0.5

        #Unit Vector Components
        UX=VX/M
        UY=VY/M
        UZ=VZ/M

        excomb[k][1] = UX
        excomb[k][2] = UY
        excomb[k][3] = UZ

    for x in range(0,p):
        k = x + 1
        excomb[k][4] = _path[x][0]
        excomb[k][5] = _path[x][1]
        excomb[k][6] = _path[x][2]
        excomb[k][7] = times[x]
        
    for x in range(1,3):
        excomb[p][x] = excomb[p-1][x]
    excomb[p][0] = p - 1



    with open(HOME+'/RRAD/src/rrad_wash_cell/src/RobotPath.csv', 'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(excomb)

        
def timestamper(_path, _points,_polar):
    global speed #units per second - will be modifiable later
    l = len(_path)
    dtime = []
    analysis = []
    tot_dist = 0
    if l == 0:
        return dtime, analysis,tot_dist

    adjustedratio = []

    if len(_points) != 0: 
        _bins = bin_points_time(_points,_path, _polar)

#    dtime.append(0)
#    timestamp.append(0)
    for x in range(1,l):
        y = x - 1
        if len(_points) == 0 or Adaptive == 2 or Adaptive == 4: 
            spd = speed
        else:
            #print "Time Adapted"
            spd = speed/4 + speed*3/4*_bins[y][1]  #aggregate impingement on segment

        dist = math.sqrt(pow(_path[x][0]-_path[y][0],2)+pow(_path[x][1]-_path[y][1],2)+pow(_path[x][2]-_path[y][2],2))
        tot_dist += dist
        dtime.append(float(dist/spd))   #add some tolerance possibly also modify to gurantee division is correct
#        timeratio.append(spd/speed)
        timeratio = 1 - float(spd/speed)
        if len(_points) != 0:
            zipmid = list(_bins[y][0])
            zipmid2 = list(_bins[y][2])
            for j in range (len(zipmid)):
                adjustedratio = float(zipmid2[j] + timeratio)
                analysis.append([zipmid[j],adjustedratio])
#        else:
#            adjustedratio.append(0)
#        timestamp.append(float(timestamp[y]+dtime[x]))

#    return timestamp
#    if len(_points) != 0: 
#        newtime = _bins[:,2]
#        for x in range(len(newtime)):
#            for y in range(len(newtime[x])):
#                newtime[x][y] = timeratio[x] 

#    if len(_points) != 0:    
#        for i in range (len(adjustedratio)):
#            zipmid = list(_bins[i][0])
#            for j in range (len(zipmid)):
#                analysis.append([zipmid[j],adjustedratio[i]])
   
        
    return dtime, analysis, tot_dist

def final_timestamper(dtimes):
    times = []
    times.append(0)
    for x in range(1,len(dtimes)):
        y = x - 1
        times.append(float(times[y]+dtimes[x]))

    return times

def centroid(p1,p2,p3):
    x = (p1[0]+p2[0]+p3[0])/3
    y = (p1[1]+p2[1]+p3[1])/3
    z = (p1[2]+p2[2]+p3[2])/3
    cent = np.asarray([x,y,z])

    return cent

def unit_vector(vector):
    if np.linalg.norm(vector) == 0:
        return vector
    uv = vector / np.linalg.norm(vector)
#    print "unit vector length",np.linalg.norm(uv)
    return uv

def impingement(v1, v2):
    #print v1, v2
    #0 = 90 degrees     1 = 0 degrees   positive values in between indicate acute angle
    # negative values indicate obtuse angles
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    val = np.dot(v1_u, v2_u)
    #print "impingement value", val
    return val

def get_polar(x,y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def magnitude(vector):
   return np.sqrt(np.dot(np.array(vector),np.array(vector)))

def norm(vector):
   return np.array(vector)/magnitude(np.array(vector))

def RayIntersect2D(rayOrigin, rayDirection, point1, point2):
    #https://gist.github.com/danieljfarrell/faf7c4cafd683db13cbc
    # Convert to numpy arrays
    rayOrigin = np.array(rayOrigin, dtype=np.float)
    rayDirection = np.array(norm(rayDirection), dtype=np.float)
    point1 = np.array(point1, dtype=np.float)
    point2 = np.array(point2, dtype=np.float)
    
    # Ray-Line Segment Intersection Test in 2D
    # http://bit.ly/1CoxdrG
    v1 = rayOrigin - point1
    v2 = point2 - point1
    v3 = np.array([-rayDirection[1], rayDirection[0]])
    t1 = np.cross(v2, v1) / np.dot(v2, v3)
    t2 = np.dot(v1, v3) / np.dot(v2, v3)
    if t1 >= 0.0 and t2 >= 0.0 and t2 <= 1.0:
        return [rayOrigin + t1 * rayDirection]
    return []

def build_convex_hull(my_mesh):
    allpoints = []
    for i in range(len(my_mesh.points)):
        allpoints.append(list(my_mesh.v0[i]))
        allpoints.append(list(my_mesh.v1[i]))
        allpoints.append(list(my_mesh.v2[i]))    
    points = np.array(allpoints)
    points*=1.01

    #viz_points(points)

    hull = ConvexHull(points,qhull_options='Fo')

    hpnts = np.asarray(hull.points)
    hfacets = np.asarray(hull.simplices)
    hnormals = np.asarray(hull.equations)
    hnormals = np.delete(hnormals,3,1)

    convexhull = mesh.Mesh(np.zeros(hfacets.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(hfacets):
        convexhull.normals[i] = hnormals[i]
        for j in range(3):
            convexhull.vectors[i][j] = hpnts[f[j],:]

    #print convexhull.normals

    #viz_mesh(convexhull)    #####Commented out for speed
##################

#    print('#################################')
#    print(hull.simplices)
#    print('#################################')
#    print(hull.neighbors)
#    print('#################################')
#    print(hull.equations)    #format is Normal{x,y,z} + [D]distance from origin to plane on the normal
                             #define plane origin as D*[X,Y,Z]
#    print('#################################')
#    print(hull.coplanar)
#    print('#################################')
#    print(hull.area)
#    print('#################################')
#    print(hull.volume)

#    print "test hull"
#    test_equations(hull.equations)

    return hull, convexhull

#    print('#################################')
#    print allpoints
#    print my_mesh.v0

def test_equations(eqtn):
    points = []
    for x in range(len(eqtn)):
        newpoint = np.asarray([eqtn[x][3]*eqtn[x][0],eqtn[x][3]*eqtn[x][1],eqtn[x][3]*eqtn[x][2]])
        points.append(newpoint)

    viz_points(points)  

def test_equation(eqtn):   #single use only
    points = []
    newpoint = np.asarray([eqtn[3]*eqtn[0],eqtn[3]*eqtn[1],eqtn[3]*eqtn[2]])
    points.append(newpoint)

    viz_points(points)

def get_centroids(_mesh):

    refpoints = []
    #loop through facets
    for i in range(len(_mesh.v0)):
    #build centroid
        ray_base = centroid(_mesh.v0[i], _mesh.v1[i], _mesh.v2[i])
        ray = _mesh.normals[i]
        refpoints.append([ray_base,ray,i])

    
    return refpoints


def main(filename):
    global minx, miny, minz, maxx, maxy, maxz, newminx, newmaxx, newminy, newmaxy, newminz, newmaxz, sprayer_width, offset, sprayer_distance, steps, speed, foundpoints, xyavg, partname
    print( 'Building Path\n')

    #sprayer_width = float(raw_input("Enter Sprayer Width: "))
    #print( sprayer_width)

    partname = filename.filename

    minx=0
    miny=0
    minz=0
    maxx=0
    maxy=0
    maxz=0

    newminx=0
    newminy=0
    newminz=0
    newmaxx=0
    newmaxy=0
    newmaxz=0

    foundpoints = 0

#        pyramid_3-sided_1_inch_solid        Water Bottleinventor        Sherman M4 Tank
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/pyramid_3-sided_1_inch_solid.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/Sherman M4 Tank.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/Water Bottleinventor.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/DiamondRemade.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/CubeDenseMesh.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/SphereDenseMesh.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/rrad_wash_cell/src/open_rim.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/rrad_wash_cell/src/pyramid_3-sided_1_inch_solid.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/rrad_wash_cell/src/Paint_Pyramid_00.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/rrad_wash_cell/src/pyramid.stl')
#    orig_mesh = mesh.Mesh.from_file(HOME+'/RRAD/src/rrad_wash_cell/src/SphereDenseMesh.stl')

    orig_mesh = mesh.Mesh.from_file(partname)
    minx, maxx, miny, maxy, minz, maxz, xyavg = find_mins_maxs(orig_mesh)
    orig_mesh, minx, maxx, miny, maxy, minz, maxz = zero(orig_mesh, minx, maxx, miny, maxy, minz, maxz)

#resizing for wayne state
#    for x in range(len(orig_mesh)):
#        orig_mesh[x][0] = orig_mesh[x][0]*3
#        orig_mesh[x][1] = orig_mesh[x][1]*3
#        orig_mesh[x][2] = orig_mesh[x][2]*3
#        orig_mesh[x][3] = orig_mesh[x][3]*3
#        orig_mesh[x][4] = orig_mesh[x][4]*3
#        orig_mesh[x][5] = orig_mesh[x][5]*3
#        orig_mesh[x][6] = orig_mesh[x][6]*3
#        orig_mesh[x][7] = orig_mesh[x][7]*3
#        orig_mesh[x][8] = orig_mesh[x][8]*3
##########

    viz_mesh(orig_mesh)    #####Commented out for speed

    run_gui(orig_mesh)

    #print sprayer_width
    minx, maxx, miny, maxy, minz, maxz, xyavg = find_mins_maxs(orig_mesh)
    orig_mesh = rotate(orig_mesh)

    ####### strip .stl
    newfile = partname.rsplit( ".", 1)[0]
    newfile = newfile + "_new.stl"

    minx=0
    miny=0
    minz=0
    maxx=0
    maxy=0
    maxz=0

    minx, maxx, miny, maxy, minz, maxz, xyavg = find_mins_maxs(orig_mesh)
    orig_mesh, minx, maxx, miny, maxy, minz, maxz = zero(orig_mesh, minx, maxx, miny, maxy, minz, maxz)
    minx, maxx, miny, maxy, minz, maxz, xyavg = find_mins_maxs(orig_mesh)
    orig_mesh.save(newfile, mode=stl.Mode.ASCII)

    orig_mesh = mesh.Mesh.from_file(newfile)

    hull, my_mesh = build_convex_hull(orig_mesh)

    print "Mesh Sizes:\nOriginal:",len(orig_mesh.normals),"\nConvex Hull:",len(my_mesh.normals)

    minx, maxx, miny, maxy, minz, maxz, xyavg = find_mins_maxs(my_mesh)
    my_mesh, minx, maxx, miny, maxy, minz, maxz = zero(my_mesh, minx, maxx, miny, maxy, minz, maxz)

    my_points = get_centroids(orig_mesh)


#    toolpath = build_toolpath(minx,maxx,miny,maxy,minz,maxz,sprayer_distance,offset,sprayer_width)
    fitpath, times, analysis = fit_to_side(my_points, my_mesh,maxz,minz,sprayer_distance,offset,sprayer_width,len(orig_mesh.normals))

#    fitpath = trim_path(ogfitpath,minx,maxx,miny,maxy,minz,maxz)
#    fitpath = optimize_points(trfitpath)
#    expath = export_toolpath(fitpath)

    simlines = point_to_line(fitpath)

    comb = combine_export(simlines,fitpath,times)
    export_path_only(simlines,fitpath,times)

#    exline = export_lines(simlines)
#    viz(fitpath,my_mesh)
#    viz(toolpath,my_mesh)
#    print toolpath

    built_path = path_to_msg(comb)
    impingement = analysis_to_msg(analysis)
    print 'found points: ',foundpoints
    print( 'Finished')
#    print fitpath

    return Path_PlannerResponse(built_path,impingement)

def path_planner():
    rospy.init_node('path_planning_server')
    s = rospy.Service('path_planner', Path_Planner, main)
    rospy.spin()

def analysis_to_msg(analysis):

    ImpingeArray = ImpingementArray()
    ImpingeArray.numberOfFacets = len(analysis)
    for x in range(len(analysis)):
        facet = Impinge()
        facet.index = analysis[x][0]
        if analysis[x][1] <= 1: facet.impinge = analysis[x][1]
        if analysis[x][1] > 1: facet.impinge = 1
        ImpingeArray.ImpingementArray.append(facet)

    with open(HOME+'/RRAD/src/rrad_wash_cell/src/ImpingementData.csv', 'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        wr.writerows(analysis)

    return ImpingeArray

def path_to_msg(path):
    #print len(path), 'initial path'
    #print path[0]

    segmentArray = LineSegmentArray()
    segmentArray.numberOfLines = len(path)-1
    for row in range(1,len(path)-1):
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
    #print path[row][0], 'row'
    #print 'segement', segment
    segment = LineSegment()
    row = (len(path)-1)
    segment.index = path[row][0]
    segment.midpointX = 10.0
    segment.midpointY = 10.0
    segment.midpointZ = 10.0
    segment.nozzleRotationX = 10.0
    segment.nozzleRotationY = 10.0
    segment.nozzleRotationZ = 10.0
    segment.pointToX = 10.0
    segment.pointToY = 10.0
    segment.pointToZ = 10.0
    segment.length = 10.0
    segment.pointX = path[row][11]
    segment.pointY = path[row][12]
    segment.pointZ = path[row][13]
    segment.times = path[row][14]
    segmentArray.lineSegmentArray.append(segment)

    #print path[row][0], 'row'
    #print 'segement', segment
    return segmentArray


if __name__ == "__main__":
    print( 'hull path planner')

    #main()
    path_planner()
