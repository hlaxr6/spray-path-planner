extends Button

func _ready():
	pass

func _on_PlayPauseButton_toggled( pressed ):
	if pressed:
		get_parent().set_move_forward()
	else:
		get_parent().set_move_stopped()
