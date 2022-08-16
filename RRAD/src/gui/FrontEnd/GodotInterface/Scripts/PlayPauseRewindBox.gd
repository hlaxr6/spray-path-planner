extends HBoxContainer

# class member variables go here, for example:
# var a = 2
# var b = "textvar"

func _ready():
	# Called every time the node is added to the scene.
	# Initialization here
	pass

func set_move_forward():
	get_parent().get_parent().get_node("Nozzle").set_move_forward()
	get_node("RewindButton").set_pressed(false)

func set_move_stopped():
	get_parent().get_parent().get_node("Nozzle").set_stop_moving()
	get_node("RewindButton").set_pressed(false)
	get_node("PlayPauseButton").set_pressed(false)
	
func set_move_backward():
	get_parent().get_parent().get_node("Nozzle").set_move_backward()
	get_node("PlayPauseButton").set_pressed(false)