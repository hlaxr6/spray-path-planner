extends VBoxContainer

var selectionCursor
var cursorWidth

func _ready():
	selectionCursor = load("res://Images/SurfaceSelectCursor.png")

func _on_RemoveButton_toggled( pressed ):
	get_parent().get_parent().get_parent().get_parent().get_node("PartViewObject").setRemoveSelected(pressed)

func _on_ClearAllButton_pressed():
	get_parent().get_parent().get_parent().get_parent().get_node("PartViewObject").clearAllSelected()

func _on_BrushWidthButton_toggled( pressed ):
	if pressed:
		get_node("BrushWidthButton/BrushWidthSlider").show()
	else:
		get_node("BrushWidthButton/BrushWidthSlider").hide()

func _on_BrushWidthSlider_value_changed( value ):
	get_parent().get_parent().get_parent().get_parent().get_node("PartViewObject").cursorWidth = value / 100
	
	selectionCursor.set_size_override(Vector2(value, value))
	#Input.set_custom_mouse_cursor(selectionCursor, Vector2(value / 2, value / 2))

func _on_SubmitSelectionButton_pressed():
	var selection = get_parent().get_parent().get_parent().get_parent().get_node("PartViewObject").getSelectedTrianglesIndexes()
	#print("selection: ", selection)
	#print(String(selection.keys()))
	#print(String(selection.values()))
	### Uncomment when ROS is updated to handle this.
	##steven edit (maybe dont need these two lines)
	#var newPath = get_node("/root/global").http_get_request("/sendSurfaceSelection", selection)
	#print("NEWPATH ",newPath)
	_write_to_file(selection)
	var pathNode = get_parent().get_parent().get_parent().get_parent().get_node("Path")
	pathNode.setNewPath(selection)

func _write_to_file(data):
# Open a file
	var file = File.new()
	if file.open("/home/steven/RRAD/src/rrad_wash_cell/src/rework_facets.txt", File.WRITE) != 0:
    	print("Error opening file")
    	return
# Save the dictionary as JSON (or whatever you want, JSON is convenient here because it's built-in)
	file.store_line(data.to_json())
	file.close()



func changeCursorToPointer():
	Input.set_custom_mouse_cursor(null)

func changeCursorToSelectionCursor():
	var partViewNode = get_parent().get_parent().get_parent().get_parent().get_node("PartViewObject")
	var width = partViewNode.cursorWidth
	if partViewNode.surfaceSelectSelected:
		Input.set_custom_mouse_cursor(selectionCursor, Vector2(width * 50, width * 50))

func _on_SurfaceSelectControls_mouse_enter():
	changeCursorToPointer()

func _on_SurfaceSelectControls_mouse_exit():
	changeCursorToSelectionCursor()

func _on_BrushWidthSlider_mouse_enter():
	changeCursorToPointer()

func _on_BrushWidthSlider_mouse_exit():
	changeCursorToSelectionCursor()

func _on_BrushWidthButton_mouse_enter():
	changeCursorToPointer()

func _on_BrushWidthButton_mouse_exit():
	changeCursorToSelectionCursor()

func _on_ClearAllButton_mouse_enter():
	changeCursorToPointer()

func _on_ClearAllButton_mouse_exit():
	changeCursorToSelectionCursor()

func _on_RemoveButton_mouse_enter():
	changeCursorToPointer()

func _on_RemoveButton_mouse_exit():
	changeCursorToSelectionCursor()

func _on_SubmitSelectionButton_mouse_enter():
	changeCursorToPointer()

func _on_SubmitSelectionButton_mouse_exit():
	changeCursorToSelectionCursor()
