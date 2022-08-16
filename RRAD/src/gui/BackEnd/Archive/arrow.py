#!/usr/bin/env python

import rospy
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class Arrow:
	"""This is the arrow that shows the position and orientation of the washer head. Moves along the path.
	Attributes:
		marker: this is the marker that represents where the head will be along the path
		currentPoint: the arrow will be either on this point or on the way to the next point
		currentPosition: the arrow's position in between the current point and the next
		positionsBetweeenPoints: fraction of the line to jump every frame, 1/positionsBetweeenPoints is true number	
		path: This is a two dementional array of position data. [row][column]
			column headers: x  y  z  rx  ry  rz
	"""

	def __init__(self, currentPointPassed, currentPositionPassed, pathPassed, numberOfPointsPassed):
		self.marker = self.makeArrow()
		self.marker.id = 3
		self.positionsBetweeenPoints = 0.1
		
		self.path = pathPassed
		self.numberOfPoints = numberOfPointsPassed
		self.currentPoint = currentPointPassed
		self.currentPosition = currentPositionPassed

		self.positionArrow()

	def getArrowToPublish(self, control):
		if control == 'forward':
			self.forwardMotion()
		elif control == 'reverse':
			self.reverseMotion()
		elif control == 'stop':
			return self.marker
		elif control[0:17] == 'absolutePosition=':
			absolutePosition = int(control[17:])
			self.setSingleNumberPosition(absolutePosition)
		else:
			print control[0:17]
			print "Arrow motion was issued wrong command"
		self.positionArrow()
		return self.marker

	def setSingleNumberPosition(self, singlePostion):
		framesPerLine = 1 / self.positionsBetweeenPoints
		self.currentPoint = int(singlePostion // framesPerLine)
		self.currentPosition = int(singlePostion % framesPerLine) 

	def forwardMotion(self):
		framesPerLine = 1 / self.positionsBetweeenPoints
		if (self.currentPosition < framesPerLine):
			self.currentPosition += 1
		else:
			if (self.currentPoint < self.numberOfPoints - 1):
				self.currentPoint += 1
			else:
				self.currentPoint = 0
			self.currentPosition = 0

	def reverseMotion(self):
		framesPerLine = 1 / self.positionsBetweeenPoints
		if (self.currentPosition > 0):
			self.currentPosition -= 1
		else:
			if (self.currentPoint > 0):
				self.currentPoint -= 1
			else:
				self.currentPoint = self.numberOfPoints - 1
			self.currentPosition = framesPerLine

	def positionArrow(self):
		xDistance = self.path[self.currentPoint + 1][0] - self.path[self.currentPoint][0]
		yDistance = self.path[self.currentPoint + 1][1] - self.path[self.currentPoint][1]
		zDistance = self.path[self.currentPoint + 1][2] - self.path[self.currentPoint][2]
		rxDistance = self.path[self.currentPoint + 1][3] - self.path[self.currentPoint][3]
		ryDistance = self.path[self.currentPoint + 1][4] - self.path[self.currentPoint][4]
		rzDistance = self.path[self.currentPoint + 1][5] - self.path[self.currentPoint][5]
		
		self.marker.pose.position.x = self.path[self.currentPoint][0] + (xDistance * self.positionsBetweeenPoints * self.currentPosition)
		self.marker.pose.position.y = self.path[self.currentPoint][1] + (yDistance * self.positionsBetweeenPoints * self.currentPosition)
		self.marker.pose.position.z = self.path[self.currentPoint][2] + (zDistance * self.positionsBetweeenPoints * self.currentPosition)
		self.marker.pose.orientation.x = self.path[self.currentPoint][3] + (rxDistance * self.positionsBetweeenPoints * self.currentPosition)
		self.marker.pose.orientation.y = self.path[self.currentPoint][4] + (ryDistance * self.positionsBetweeenPoints * self.currentPosition)
		self.marker.pose.orientation.z = self.path[self.currentPoint][5] + (rzDistance * self.positionsBetweeenPoints * self.currentPosition)
		
	def getDistance(self):
		framesPerLine = 1 / self.positionsBetweeenPoints
		return framesPerLine * (self.numberOfPoints  - 1)

	def getSingleNumberPosition(self):
		framesPerLine = 1 / self.positionsBetweeenPoints
		pos = self.currentPoint * framesPerLine
		pos += self.currentPosition
		return pos

	def makeArrow(self):
		arrow = Marker()
		arrow = self.setBasicMarkerData(arrow)
		arrow.type = 0
		arrow = self.setArrowScale(arrow)
		arrow = self.turnMarkerGreen(arrow)
		return arrow

	def setBasicMarkerData(self, mark):
		mark.header.frame_id = "base_link"
		mark.header.stamp = rospy.get_rostime()
		mark.ns = "add_markers"
		mark.action = 0 #ADD
		mark.pose.orientation.w = 1.0
		return mark

	def setArrowScale(self, arrow):
		arrow.scale.x = 0.15
		arrow.scale.y = 0.05
		arrow.scale.z = 0.05
		return arrow

	def turnMarkerGreen(self, mark):
		mark.color.g = 1.0;
		mark.color.a = 1.0;
		return mark