extends Button

func _ready():
	pass

func _on_RewindButton_toggled( pressed ):
	if pressed:
		get_parent().set_move_backward()
	else:
		get_parent().set_move_stopped()
