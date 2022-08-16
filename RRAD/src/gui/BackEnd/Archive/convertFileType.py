#!/usr/bin/python3.5
import bpy
import os

class FileTypeConverter():

	def __init__(self):
		self.path = os.getcwd()

	def convertStlToObj(filenameStl, filenameObj):
		stlPath = self.path + filenameStl
		bpy.ops.import_mesh.stl(filepath=stlPath, axis_forward='Z', axis_up='Y')

		objPath = self.path + filenameObj
		bpy.ops.import_mesh.stl(filepath=objPath, axis_forward='Z', axis_up='Y')


## UNIT TEST ##
if __name__ == '__main__':
	converter = FileTypeConverter()
	converter.convertStlToObj("BlenderConversion/SphereDenseMesh.stl", "BlenderConversion/SphereDenseMesh.obj")

