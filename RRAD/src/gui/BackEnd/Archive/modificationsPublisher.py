import rospy
from path_publisher.srv import segment_modification

def handle_modifications_server():
	rospy.init_node('segment_modification_server')
	service = rospy.Service('modifications', segment_modification, send_back_new_path)

	rospy.spin()

def send_back_new_path(request):
	# use request data to deliver new path
	# for now, it just returns what it receives
	return request.jsonModifications

if __name__ == "__main__":
	handle_modifications_server()