extends MeshInstance

const SCALE = 0.15

var triangles = []
var surfTool

func _ready():
	pass

func setTriangles(newTriangles, impingementData):
	surfTool = SurfaceTool.new()
	var mesh = Mesh.new()
	var dataTool = MeshDataTool.new()
	var material = FixedMaterial.new()
	var selectedTriangles = []
	material.set_fixed_flag(FixedMaterial.FLAG_USE_COLOR_ARRAY, true)
	surfTool.set_material(material)
	
	triangles = vectorizePointArrays(newTriangles, impingementData)
	triangles = resize(triangles)
	surfTool.begin(VisualServer.PRIMITIVE_TRIANGLES)
	for triangle in triangles:
		changeColor(triangle, selectedTriangles)
		surfTool.add_normal(triangle['normal'])
		surfTool.add_vertex(triangle["vertex1"])
		surfTool.add_vertex(triangle["vertex2"])
		surfTool.add_vertex(triangle["vertex3"])
	surfTool.index()
	surfTool.commit(mesh)
	self.set_mesh(mesh)
	get_parent().addShapes(mesh)

func refreshMesh(selectedTriangles):
	surfTool = SurfaceTool.new()
	var mesh = Mesh.new()
	var material = FixedMaterial.new()
	material.set_fixed_flag(FixedMaterial.FLAG_USE_COLOR_ARRAY, true)
	surfTool.set_material(material)
	surfTool.begin(VisualServer.PRIMITIVE_TRIANGLES)
	for triangle in triangles:
		changeColor(triangle, selectedTriangles)
		surfTool.add_normal(triangle["normal"])
		surfTool.add_vertex(triangle["vertex1"])
		surfTool.add_vertex(triangle["vertex2"])
		surfTool.add_vertex(triangle["vertex3"])
	surfTool.index()
	surfTool.commit(mesh)
	self.set_mesh(mesh)

func changeColor(triangle, selectedTriangles):
	if selectedTriangles.has(triangle):
		surfTool.add_color(Color(1, 0, 1))
	else:
		surfTool.add_color(triangle["color"])

func vectorizePointArrays(triangles, impingementData):
	var newTriangles = []
	print("TESTING TRIANGLES")
	print(triangles.keys())
	for key in triangles.keys():
		var triangle = triangles[key]
		triangle["normal"] = buildVector(triangle["normal"])
		triangle["originalvertex1"] = buildReturnVector(triangle["vertex1"])
		triangle["originalvertex2"] = buildReturnVector(triangle["vertex2"])
		triangle["originalvertex3"] = buildReturnVector(triangle["vertex3"])
		triangle["vertex1"] = buildVector(triangle["vertex1"])
		triangle["vertex2"] = buildVector(triangle["vertex2"])
		triangle["vertex3"] = buildVector(triangle["vertex3"])

		var colorVal = impingementData[int(key)]
		var sum = triangle["vertex1"] + triangle["vertex2"] + triangle["vertex3"]
		triangle["center"] = sum / 3
		triangle["color"] = impingementValueToColor(colorVal)
		triangle["impingementValue"] = colorVal
		triangle["index"] = key
		if int(key) == 20:
			print(triangle["vertex1"], triangle["vertex2"], triangle["vertex3"])
		newTriangles.append(triangle)
	return newTriangles

func makeDummyColorValue(triangle):
	var direction = Vector3(1,1,1)
	direction = direction.normalized()
	var normal = triangle["normal"]
	normal = normal.normalized()
	var color = normal.dot(direction)
	color = abs(color)
	return color

func buildVector(array):
	return Vector3(array[0], array[2], array[1])

func buildReturnVector(array):
	return Vector3(array[0], array[1], array[2])

func resize(triangles):
	for triangle in triangles:
		triangle["normal"] = triangle["normal"] * SCALE
		triangle["vertex1"] = triangle["vertex1"] * SCALE
		triangle["vertex2"] = triangle["vertex2"] * SCALE
		triangle["vertex3"] = triangle["vertex3"] * SCALE
		triangle["center"] = triangle["center"] * SCALE
	return triangles

func impingementValueToColor(value):
	var minimum = 0
	var maximum = 1
	var ratio = 2 * (value - minimum) / (maximum - minimum)
	var blue = max(0, (1 - ratio))
	var red = max(0, (ratio - 1))
	var green = 1 - blue - red
	return Color(red, green, blue)

func monochromeImpingementValueToColor(value):
	var color = Color(value, value, 0)
	return color
	