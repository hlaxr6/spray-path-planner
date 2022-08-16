#!/usr/bin/env python

import numpy
from stl import mesh

class TriangleListBuilder():

	def __init__(self, filename):
		self.triangles = {}
		self.mesh = mesh.Mesh.from_file(filename)
		minx, maxx, miny, maxy, minz, maxz = self.find_mins_maxs()
		minx, maxx, miny, maxy, minz, maxz = self.zero(minx, maxx, miny, maxy, minz, maxz)
		self.makeTriangleList()

	def makeTriangleList(self):
		for facet in range(len(self.mesh.units)):
			vertex1 = self.buildVertex(self.mesh[facet][0:3])
			vertex2 = self.buildVertex(self.mesh[facet][3:6])
			vertex3 = self.buildVertex(self.mesh[facet][6:9])
			normal = self.buildVertex(self.mesh.normals[facet])
			self.triangles[facet] = self.buildTriangle(vertex1, vertex2, vertex3, normal)

	def buildVertex(self, numpyArray):
		vertex = []
		vertex.append(numpyArray[0].item())
		vertex.append(numpyArray[1].item())
		vertex.append(numpyArray[2].item())
		return vertex

	def buildTriangle(self, vertex1, vertex2, vertex3, normal):
		triangle = {}
		triangle["vertex1"] = vertex1
		triangle["vertex2"] = vertex2
		triangle["vertex3"] = vertex3
		triangle["originalvertex1"] = vertex1
		triangle["originalvertex2"] = vertex2
		triangle["originalvertex3"] = vertex3
		triangle["normal"] = normal
		return triangle

	def getTriangles(self):
		if (self.triangles):
			return self.triangles
		else:
			return False

	def zero(self, minx, maxx, miny, maxy, minz, maxz):
	    difx = 0 - (minx + ((maxx-minx)/2))
	    dify = 0 - (miny + ((maxy-miny)/2))
	    difz = 0 - (minz + ((maxz-minz)/2))
	    minx = minx + difx
	    miny = miny + dify
	    minz = minz + difz
	    maxx = maxx + difx
	    maxy = maxy + dify
	    maxz = maxz + difz
	    self.mesh.x += difx
	    self.mesh.y += dify
	    self.mesh.z += difz

	    return minx, maxx, miny, maxy, minz, maxz
	
	def find_mins_maxs(self):
	    minx=0
	    miny=0
	    minz=0
	    maxx=0
	    maxy=0
	    maxz=0
	    for p in self.mesh.points:
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
	    #print minx, maxx, miny, maxy, minz, maxz
	    return minx, maxx, miny, maxy, minz, maxz

if __name__ == "__main__":
	#builder = TriangleListBuilder("/home/local/GACL/gharms/catkin_ws_ur/src/gui/Backend/SphereDenseMesh.stl")
	builder.makeTriangleList()
