#!/usr/bin/env python
import rospy
import path_publisher
from path_publisher.msg import LineSegmentArray, LineSegment
from csv_reader import CSV_Reader

def talker():
	pub = rospy.Publisher('path', LineSegmentArray, queue_size=1000, latch=True)
	rospy.init_node('publisher', anonymous=True)
	reader = CSV_Reader()
	reader.getData()

	segmentArray = LineSegmentArray()

	if not rospy.is_shutdown():
		segmentArray.numberOfLines = reader.getLength() - 1
		for row in range(reader.getLength()):
			segment = LineSegment()
			segment.index = reader.getPositionByAxis(row, 0)
			segment.midpointX = reader.getPositionByAxis(row, 1)
			segment.midpointY = reader.getPositionByAxis(row, 2)
			segment.midpointZ = reader.getPositionByAxis(row, 3)
			segment.nozzleRotationX = reader.getPositionByAxis(row, 4)
			segment.nozzleRotationY = reader.getPositionByAxis(row, 5)
			segment.nozzleRotationZ = reader.getPositionByAxis(row, 6)
			segment.pointToX = reader.getPositionByAxis(row, 7)
			segment.pointToY = reader.getPositionByAxis(row, 8)
			segment.pointToZ = reader.getPositionByAxis(row, 9)
			segment.length = reader.getPositionByAxis(row, 10)
			segment.pointX = reader.getPositionByAxis(row, 11)
			segment.pointY = reader.getPositionByAxis(row, 12)
			segment.pointZ = reader.getPositionByAxis(row, 13)
			segmentArray.lineSegmentArray.append(segment)
		
		print segmentArray
		pub.publish(segmentArray)

if __name__ == '__main__':
	talker()
	rospy.spin()