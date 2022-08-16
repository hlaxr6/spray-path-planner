extends Button

func _ready():
	is_toggle_mode()

func _on_SelectSurfaceButton_toggled( pressed ):
	get_parent().get_parent().get_parent().get_node("PartViewObject").setSurfaceSelectSelected(pressed)
	if pressed:
		var cursor = get_node("SurfaceSelectControls").selectionCursor
		Input.set_custom_mouse_cursor(cursor)
		get_node("SurfaceSelectControls").show()
	else:
		Input.set_custom_mouse_cursor(null)
		get_node("SurfaceSelectControls").hide()