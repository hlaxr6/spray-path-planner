#!/usr/bin/env python

import rospy
import time
from std_msgs.msg import String
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from pathListener import PathListener
from arrow import Arrow
from threading import Event

class Add_Markers():
	"""This publishes tool path data to RViz

	Attributes:
		velocity: fraction of each line to jump each frame
		currentPoint: point vector at which the arrow is currently iterating though
		currentPositionBetweenPoints: current position on the path between points
		arrow: holds an Arrow object to be modified outside the update loop
		path: This is a two dementional array of position data. [row][column]
			column headers: x  y  z  rx  ry  rz
		numberOfPoints: this is how many positions there are along the path
	"""

	def __init__(self):
		self.currentPoint = 0
		self.currentPositionBetweenPoints = 0

		self.path = self.getPath()

		rospy.init_node('add_markers')
		self.markerPub = rospy.Publisher('visualization_marker', Marker, queue_size=10)
		rate = rospy.Rate(30)

		self.arrow = Arrow(self.currentPoint, self.currentPositionBetweenPoints, self.path, self.numberOfPoints)

	def update (self, control):
		if not rospy.is_shutdown():
			point = self.makePoint()
			point.id = 0
			line = self.makeLine()
			line.id = 1

			self.positionPointsAndLines(point, line)
			self.markerPub.publish((self.arrow.getArrowToPublish(control)))
			rospy.sleep(.05)

	def getPath(self):
		stopFlag = Event()
		pathPoints = PathListener(stopFlag)
		pathPoints.start()
		while pathPoints.complete is False:
			time.sleep(1)
		stopFlag.set()
		pathPoints.join()
		self.numberOfPoints = pathPoints.getLength()
		return pathPoints.getPath()

	def getArrowDistance(self):
		return self.arrow.getDistance()

	def getArrowSingleNumberPosition(self):
		return self.arrow.getSingleNumberPosition()

	def setBasicMarkerData(self, mark):
		mark.header.frame_id = "base_link"
		mark.header.stamp = rospy.get_rostime()
		mark.ns = "add_markers"
		mark.action = 0 #ADD
		mark.pose.orientation.w = 1.0
		return mark

	def setPointsScale(self, point):
		point.scale.x = 0.005
		point.scale.y = 0.005
		return point

	def setLinesScale(self, line):
		line.scale.x = 0.005
		return line

	def turnMarkerGreen(self, mark):
		mark.color.g = 1.0;
		mark.color.a = 1.0;
		return mark

	def turnMarkerRed(self, mark):
		mark.color.r = 1.0;
		mark.color.a = 1.0;
		return mark

	def positionPointsAndLines(self, point, line):
		startPoint = Point()
		endPoint = Point()
		for i in range(self.numberOfPoints + 1):
			pointPosition = Point()
			pointPosition.x = self.path[i][0]
			pointPosition.y = self.path[i][1]
			pointPosition.z = self.path[i][2]
			point.points.append(pointPosition)
			line.points.append(pointPosition)

		self.markerPub.publish(point)
		self.markerPub.publish(line)

	def makePoint(self):
		point = Marker()
		point = self.setBasicMarkerData(point)
		point.type = 8
		point = self.setPointsScale(point)
		point = self.turnMarkerGreen(point)
		return point

	def makeLine(self):
		line = Marker()
		line = self.setBasicMarkerData(line)
		line.type = 4
		line = self.setLinesScale(line)
		line = self.turnMarkerRed(line)
		return line

if __name__ == '__main__':
	markerMaker = Add_Markers()
	markerMaker.arrow.setArrowMotionForward()
	while True:
		markerMaker.update("forward")