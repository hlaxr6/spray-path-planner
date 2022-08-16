#!/usr/bin/env python
PKG = 'path_publisher'
import time

import rospy
import roslib; roslib.load_manifest(PKG)
import path_publisher
from path_publisher.msg import LineSegmentArray

class PathListener():

	def __init__(self):
		rospy.init_node('add_markers')
		self.sub = rospy.Subscriber("path", LineSegmentArray, self.callback)
		self.length = 0
		self.i = 0
		self.path = []
		self.complete = False

	def callback(self, segments):
		self.length = segments.numberOfLines
		segmentArray = segments.lineSegmentArray
		for index in range(self.length + 1):
			self.path.append(segmentArray[index].index)
			self.path.append(segmentArray[index].midpointX)
			self.path.append(segmentArray[index].midpointY)
			self.path.append(segmentArray[index].midpointZ)
			self.path.append(segmentArray[index].nozzleRotationX)
			self.path.append(segmentArray[index].nozzleRotationY)
			self.path.append(segmentArray[index].nozzleRotationZ)
			self.path.append(segmentArray[index].pointToX)
			self.path.append(segmentArray[index].pointToY)
			self.path.append(segmentArray[index].pointToZ)
			self.path.append(segmentArray[index].length)
			self.path.append(segmentArray[index].pointX)
			self.path.append(segmentArray[index].pointY)
			self.path.append(segmentArray[index].pointZ)

		print self.path
		self.complete = True
		self.sub.unregister()

	def run(self):
		while not self.complete:
			rospy.wait_for_message("path", LineSegmentArray)

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

if __name__ == '__main__':
	stopFlag = Event()
	listener = PathListener(stopFlag)
	listener.start()
	while listener.complete is False:
		time.sleep(1)
	listener.join()
	listener.getPath()
	for i in range(listener.i):
		print listener.path[i]
		print i
	print listener.getPosition(0,2)