#Impingement Model

import time
import csv as csv 
import numpy as np
from stl import mesh
from math import (acos, degrees)
from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ImpingementModel():

    def __init__(self):
        pass

    def createImpingementData(self, meshFile):
        #Variable def'ns for path plan points
        index1 = 0
        delt = 0.1
        t2=0
        X2=0
        VX=0
        VY=0
        VZ=0

        T=[]
        X=[]
        Y=[]
        Z=[]
        NX=[]
        NY=[]
        NZ=[]
        UV=[]

        #Import part file
        part = mesh.Mesh.from_file(meshFile)


        #Import/Modify path plan
        while True:
            csv_file_object = csv.reader(open('/home/steven/RRAD/src/rrad_wash_cell/src/PathPlan.csv','rb'))
            header = csv_file_object.next()
            index2 = index1+1
            data = []
            for row in csv_file_object:
                data.append(row)
            data = np.array(data)

        #--------------------------------------------------

            #Path Plan Point X,Y,Z values
            X1 = float(data[index1,11])
            Y1 = float(data[index1,12])
            Z1 = float(data[index1,13])
            t1 = float(data[index1,14])

            X3 = float(data[index2,11])
            Y3 = float(data[index2,12])
            Z3 = float(data[index2,13])
            t3 = float(data[index2,14])

        #Nozzle X,Y,Z Values
            NX1 = float(data[index1,4])
            NY1 = float(data[index1,5])
            NZ1 = float(data[index1,6])

            if (index2 == 418):
                break

            NX3 = float(data[index2,4])
            NY3 = float(data[index2,5])
            NZ3 = float(data[index2,6])


            #Print the first value separately
            if t1==0:
                T.append(t1)
                X.append(X1)
                Y.append(Y1)
                Z.append(Z1)
                NX.append(NX1)
                NY.append(NY1)
                NZ.append(NZ1)

            #For the values within timestamp index
            #The greatest timestamp gap I see is less than 2 seconds - found 40 by trial and error
            for j in range(40):
                if t2>=t1 and t2<=t3:
                    t2+=delt

                    #Interpolation
                    X2 = ((t2-t1)*(X3-X1)) / (t3-t1) + X1
                    Y2 = ((t2-t1)*(Y3-Y1)) / (t3-t1) + Y1
                    Z2 = ((t2-t1)*(Z3-Z1)) / (t3-t1) + Z1

                    NX2 = ((t2-t1)*(NX3-NX1)) / (t3-t1) + NX1
                    NY2 = ((t2-t1)*(NY3-NY1)) / (t3-t1) + NY1
                    NZ2 = ((t2-t1)*(NZ3-NZ1)) / (t3-t1) + NZ1

                    #Find the reverse vector between Point and Nozzle
                    #This will be used to calculate theta between facet normal and spray vector

                    #Reverse vector - Subtract the nozzleX,Y,Z from the pointX,Y,Z   Nozzle---->Point
                    VX=X2-NX2
                    VY=Y2-NY2
                    VZ=Z2-NZ2

                    #Find Unit Vectors - magnitudes, then UnitV = Vector / sqrt(magnitude)
                    M=(VX**2+VY**2+VZ**2)**0.5

                    UX=VX/M
                    UY=VY/M
                    UZ=VZ/M

                    #Unit Vector for Path Plan - combine values
                    U = [UX, UY, UZ]

                    #Path Plan -- Time, Point and Nozzle Values
                    T.append(t2)
                    X.append(X2)
                    Y.append(Y2)
                    Z.append(Z2)
                    NX.append(NX2)
                    NY.append(NY2)
                    NZ.append(NZ2)
                    UV.append(U)
                  
                j+=1
            index1 += 1

        UV.append(U)

        #FOR GRAPHING
        X_Facgraph = []
        Y_Facgraph = []
        Z_Facgraph = []

        X_Facgraph = X
        Y_Facgraph = Y
        Z_Facgraph = Z

        #Loop through all facets in part and find the angles between facet normals and path plan vectors
        Impinge=[]

        facets = len(part.units)
        matches = 0
        Max_Value_Ang = []
        Max_Value_Dist = []
        Facet_Value = []

        for f in range(facets):
            
            Max_Value_Ang.append(0)
            Max_Value_Dist.append(0)
            Facet_Value.append(0)

            Point = part.points[f]

            #Vertex points for each facet triangle
            X1 = Point[0]
            X2 = Point[3]
            X3 = Point[6]
            Y1 = Point[1]
            Y2 = Point[4]
            Y3 = Point[7]
            Z1 = Point[2]
            Z2 = Point[5]
            Z3 = Point[8]

            #Need to figure out when to compare nozzle values
            #Currently this makes a cube around a facet, not a great evaluation...
            ext = 0
            maxX = max(X1, X2, X3) + ext
            #minX = min(X1, X2, X3) - ext
            CX = (X1+X2+X3)/3
            maxY = max(Y1, Y2, Y3) + ext
            #minY = min(Y1, Y2, Y3) - ext
            CY = (Y1+Y2+Y3)/3
            maxZ = max(Z1, Z2, Z3) + ext
            #minZ = min(Z1, Z2, Z3) - ext
            CZ = (Z1+Z2+Z3)/3

            Norm = part.units[f]
            NormX = Norm[0]
            NormY = Norm[1]
            NormZ = Norm[2]

            rad = max(maxX-CX, maxY-CY, maxZ-CZ)

            #Now loop through the path plan points
            PPPoints = len(T)
            for k in range(PPPoints):
                DiffX = NX[k]-CX
                DiffY = NY[k]-CY
                DiffZ = NZ[k]-CZ
                Eq2 = NormX*DiffX + NormY*DiffY + NormZ*DiffZ

                #Define a circle on the plane of the facet
                if (DiffX**2 + DiffY**2 + DiffZ**2 <= rad**2):
                    if np.logical_and(Eq2 >= -1, Eq2 <= 1) == True:
                    
                        C = dot(UV[k],part.units[f])
                        Angle = arccos(clip(C, -1,1))

                        if Angle <= 1.4: #80 degrees
                            Value_Ang = 1 - .714*Angle

                            dist = (DiffX**2 + DiffY**2 + DiffZ**2)**0.5
                            Value_dist = 1 - dist/rad

                            if (Value_Ang >= Max_Value_Ang[f]):
                                Max_Value_Ang[f]=Value_Ang

                            if (Value_dist >= Max_Value_Dist[f]):
                                Max_Value_Dist[f]=Value_dist

                            Facet_Value[f] = Max_Value_Dist[f]*Max_Value_Ang[f]
                            matches +=1

                        else:
                            print("Vector comparison out of useful range")

        #check = raw_input('Break###############')
        return Facet_Value 
               
        #UNCOMMENT FOR GRAPHING

        #     if Max_Value_Ang[f] >= 0.1:

        #         X_Facgraph.append(X1)
        #         X_Facgraph.append(X2)
        #         X_Facgraph.append(X3)
        #         Y_Facgraph.append(Y1)
        #         Y_Facgraph.append(Y2)
        #         Y_Facgraph.append(Y3)
        #         Z_Facgraph.append(Z1)
        #         Z_Facgraph.append(Z2)
        #         Z_Facgraph.append(Z3)

        # #This prints every facet vertex as a point...
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # #ax.quiver(NX, NY, NZ, UV[1], UV[2], UV[3])
        # ax.scatter(X_Facgraph,Y_Facgraph,Z_Facgraph)
        # ax.set_xlim([-100, 100])
        # ax.set_ylim([-100, 100])
        # ax.set_zlim([-100, 100])
        # plt.show()
