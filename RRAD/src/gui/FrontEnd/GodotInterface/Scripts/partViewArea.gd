extends RigidBody

var selectedTriangles = []
var dragging = false
var mousePos

var surfaceSelectSelected = false
var removeSelected = false
var cursorWidth = .5

func _ready():
	set_process(true)

func _process(delta):
	if dragging:
		var surfaceClick = mousePos - get_translation()
		var triangles = get_node("PartViewMesh").triangles
		if surfaceSelectSelected and not removeSelected:
			var dragSelection = []
			var closestTriangle = getClosestTriangle(triangles, surfaceClick)
			checkIfContiguousInRange(triangles, closestTriangle, dragSelection, surfaceClick)
			for selection in dragSelection:
				selectedTriangles.append(selection)
			get_node("PartViewMesh").refreshMesh(selectedTriangles)
		if removeSelected:
			var dragSelection = []
			var closestTriangle = getClosestTriangle(triangles, surfaceClick)
			checkIfContiguousInRange(triangles, closestTriangle, dragSelection, surfaceClick)
			for selection in dragSelection:
				selectedTriangles.erase(selection)
			get_node("PartViewMesh").refreshMesh(selectedTriangles)

func checkIfContiguousInRange(triangles, triangle, selection, surfaceClick):
	if not selection.has(triangle):
		selection.append(triangle)
		for possibleTriangle in triangles:
			var possiblePoints = []
			possiblePoints.append(possibleTriangle["vertex1"])
			possiblePoints.append(possibleTriangle["vertex2"])
			possiblePoints.append(possibleTriangle["vertex3"])
			if isWithinBrushWidth(surfaceClick, possibleTriangle) and possiblePoints.has(triangle["vertex1"]) and not isEdge(possibleTriangle, triangle):
				checkIfContiguousInRange(triangles, possibleTriangle, selection, surfaceClick)
			if isWithinBrushWidth(surfaceClick, possibleTriangle) and possiblePoints.has(triangle["vertex2"]) and not isEdge(possibleTriangle, triangle):
				checkIfContiguousInRange(triangles, possibleTriangle, selection, surfaceClick)
			if isWithinBrushWidth(surfaceClick, possibleTriangle) and possiblePoints.has(triangle["vertex3"]) and not isEdge(possibleTriangle, triangle):
				checkIfContiguousInRange(triangles, possibleTriangle, selection, surfaceClick)

func isWithinBrushWidth(surfaceClick, possibleTriangle):
	var cameraPosition = get_parent().get_node("Path/RotationPitch/RotationYaw/Camera").get_translation()
	var distanceToSurface = cameraPosition.distance_to(surfaceClick)
	
	if possibleTriangle["center"].distance_to(surfaceClick) < cursorWidth * distanceToSurface * .05:
		return true
	else:
		return false

func isEdge(possibleTriangle, currentTriangle):
	var angle = possibleTriangle["normal"].angle_to(currentTriangle["normal"])
	if angle > PI/6:
		return true
	else:
		return false

func getClosestTriangle(triangles, surfaceClick):
	var closestTriangle
	for triangle in triangles:
		if closestTriangle == null or triangle["center"].distance_to(surfaceClick) < closestTriangle["center"].distance_to(surfaceClick) and isOnPlane(triangle, surfaceClick):
			closestTriangle = triangle
	return closestTriangle

func isOnPlane(triangle, surfaceClick):
	var plane = Plane(triangle["vertex1"], triangle["vertex2"], triangle["vertex3"])
	if plane.has_point(surfaceClick, 0.001):
		return true
	else:
		return false

func addShapes(mesh):
	var shape = mesh.create_trimesh_shape()
	add_shape(shape)

func _on_PartViewObject_input_event( camera, event, click_pos, click_normal, shape_idx ):
	if event.type == InputEvent.MOUSE_BUTTON:
		if event.pressed and event.button_index == BUTTON_LEFT:
			dragging = true
		elif not event.pressed and event.button_index == BUTTON_LEFT:
			dragging = false
		
	mousePos = click_pos

func setSurfaceSelectSelected(selected):
	surfaceSelectSelected = selected

func setRemoveSelected(selected):
	removeSelected = selected

func clearAllSelected():
	selectedTriangles = []
	get_node("PartViewMesh").refreshMesh(selectedTriangles)

func getSelectedTrianglesIndexes():
	var selection = {}
	var triangleList = get_node("PartViewMesh").triangles
	for index in range(triangleList.size()):
		if selectedTriangles.has(triangleList[index]):
			var triangle = triangleList[index]
			selection[index] =[triangle["originalvertex1"],triangle["originalvertex2"],triangle["originalvertex3"]]
	return selection