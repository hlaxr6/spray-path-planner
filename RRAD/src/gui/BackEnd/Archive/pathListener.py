#!/usr/bin/env python
PKG = 'path_publisher'
import time

import rospy
import roslib; roslib.load_manifest(PKG)
import path_publisher
from threading import Thread, Event
from path_publisher.msg import Floats

class PathListener(Thread):
## pass an Event() into the event arguement to stop this thread. 


	def __init__(self, event):
		Thread.__init__(self)
		rospy.init_node('add_markers')
		sub = rospy.Subscriber("path", Floats, self.callback)
		self.length = 0
		self.i = 0
		self.path = []
		self.path.append([])
		self.stopped = event
		self.complete = False

	def callback(self, points):
		self.length = points.length
		allPoints = points.data
		for index in range(self.length + 1):
			print allPoints[0:6]
			self.path.append([])
			self.path[index].append(allPoints[0])
			self.path[index].append(allPoints[1])
			self.path[index].append(allPoints[2])
			self.path[index].append(allPoints[3])
			self.path[index].append(allPoints[4])
			self.path[index].append(allPoints[5])
			allPoints = allPoints[6:]

		print 
		self.complete = True

	def run(self):
		while not self.stopped.isSet() and not self.complete:
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