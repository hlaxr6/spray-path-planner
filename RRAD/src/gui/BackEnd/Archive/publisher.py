#!/usr/bin/env python
import rospy
import path_publisher
from path_publisher.msg import Floats
from csv_reader import CSV_Reader

def talker():
	pub = rospy.Publisher('path', Floats, queue_size=1000, latch=True)
	rospy.init_node('publisher', anonymous=True)
	reader = CSV_Reader()
	reader.getData()

	path = Floats()

	if not rospy.is_shutdown():
		path.index = 0
		path.length = reader.getLength() - 1
		point = []
		for row in range(reader.getLength()):
			for column in range(6):
				point.append(reader.getPositionByAxis(row, column))
		path.data = point
		
		print point
		pub.publish(path)

if __name__ == '__main__':
	try:
		talker()
		rospy.spin()
	except rospy.ROSInterruptException:
		pass
