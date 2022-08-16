#!/usr/bin/env python
PKG = 'path_publisher'
import time

import rospy
import roslib; roslib.load_manifest(PKG)
import path_publisher
from path_publisher.msg import Floats

class PathListener():

	def __init__(self):
		rospy.init_node('add_markers')
		self.sub = rospy.Subscriber("path", Floats, self.callback)
		self.length = 0
		self.i = 0
		self.path = []
		self.complete = False

	def callback(self, points):
		self.length = points.length
		allPoints = points.data
		for index in range(self.length + 1):
			print allPoints[0:6]
			self.path.append(allPoints[0])
			self.path.append(allPoints[1])
			self.path.append(allPoints[2])
			self.path.append(allPoints[3])
			self.path.append(allPoints[4])
			self.path.append(allPoints[5])
			allPoints = allPoints[6:]

		self.complete = True
		self.sub.unregister()

	def run(self):
		while not self.complete:
			rospy.wait_for_message("path", Floats)

	def getLength(self):
		return self.length
	
	def getPath(self):
		if not self.complete:
			print "Not finished gathering data"
		else:
			self.i = 0
			self.complete = False
			return self.path

	def getPosition(self, row, column):
		return self.path[row][column]