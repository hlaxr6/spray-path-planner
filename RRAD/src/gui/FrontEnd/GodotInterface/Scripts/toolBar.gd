extends HBoxContainer

func _ready():
	pass


func _on_FrontView_pressed():
	var cameraNode = get_parent().get_node("RotationPitch")
	cameraNode.set_camera_front()

func _on_TopView_pressed():
	var cameraNode = get_parent().get_node("RotationPitch")
	cameraNode.set_camera_top()

func _on_IsometricView_pressed():
	var cameraNode = get_parent().get_node("RotationPitch")
	cameraNode.set_camera_isometric()