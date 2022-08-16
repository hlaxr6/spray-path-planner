extends HSlider

var touched = false

func _ready():
	set_process(true)

func _process(delta):
	if !touched:
		var numberOfPositions = get_parent().get_parent().get_parent().numberOfPositions - 2
		var nozzleNode = get_parent().get_parent().get_parent().get_node("Nozzle")
		var value = nozzleNode.activePoint + nozzleNode.deltaCount
		
		set_max(numberOfPositions)
		set_ticks(numberOfPositions)
		set_value(value)



func _on_NozzleSlider_input_event( ev ):
	if ev.type == InputEvent.MOUSE_BUTTON:
		touched = ev.is_pressed()
	if ev.type == InputEvent.MOUSE_MOTION:
		if touched:
			get_parent().set_move_stopped()
			var value = get_value()
			var delta = value - int(value)
			var activePoint = int(value)
			
			var nozzleNode = get_parent().get_parent().get_parent().get_node("Nozzle")
			nozzleNode.set_position_from_slider(activePoint, delta)