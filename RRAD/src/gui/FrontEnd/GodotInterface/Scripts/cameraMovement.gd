extends Spatial

var mouse_pressed_rotate = false
var mouse_presseed_pan = false
var last_position = Vector2()

func _ready():
	set_process_input(true)

func _input(event):
	if event.type == InputEvent.MOUSE_BUTTON:
		if event.is_action("camera_rotate"):
			mouse_pressed_rotate = event.is_pressed()
		if event.is_action("camera_pan"):
			mouse_presseed_pan = event.is_pressed()
		if mouse_pressed_rotate or mouse_presseed_pan:
			last_position = event.pos
			
	elif event.type == InputEvent.MOUSE_MOTION:
		var delta = event.pos - last_position
		if mouse_pressed_rotate:
			last_position = event.pos
			var rotationYawNode = get_node("RotationYaw")
			rotationYawNode.rotate_x(-delta.y * 0.01)
			if(rotationYawNode.get_rotation().x < -1.5):
				rotationYawNode.set_rotation(Vector3(-1.5, 0, 0))
			if(rotationYawNode.get_rotation().x > 1.5):
				rotationYawNode.set_rotation(Vector3(1.5, 0, 0))
			rotate_y(-delta.x * 0.01)
		elif mouse_presseed_pan:
			last_position = event.pos
			self.translate(Vector3(-delta.x * .1, delta.y * .1, 0))
			
	if event.is_action("camera_zoom_in"):
		get_node("RotationYaw/Camera").translate(Vector3(0,0,-1))
	if event.is_action("camera_zoom_out"):
		get_node("RotationYaw/Camera").translate(Vector3(0,0,1))
		
func set_camera_front():
	set_rotation(Vector3(0,0,0))
	set_translation(Vector3(0,0,0))
	get_node("RotationYaw").set_rotation(Vector3(0,0,0))

func set_camera_top():
	set_rotation(Vector3(0,0,0))
	set_translation(Vector3(0,0,0))
	get_node("RotationYaw").set_rotation(Vector3(-1.75,0,0))

func set_camera_isometric():
	set_rotation(Vector3(0,-0.6,0))
	set_translation(Vector3(0,0,0))
	get_node("RotationYaw").set_rotation(Vector3(-0.6,0,0))