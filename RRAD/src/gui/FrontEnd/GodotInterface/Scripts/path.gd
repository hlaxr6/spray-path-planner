extends ImmediateGeometry

const NUMBER_OF_ROWS_IN_PATH_DATA = 15
const PATH_SCALE = 0.15

var midpointArray = []
var pointToArray = []
var lengthArray = []
var pointArray = []
var timeArray = []
var nozzleRotationArray = []
var numberOfPositions

func setNewPath(newPath):
	var pathText
	if newPath == "startup":
		var responseJSON = get_node("/root/global").http_get_request("/getPath", "")
		var responseDictionary = Dictionary()
		responseDictionary.parse_json(responseJSON)
		pathText = responseDictionary["path"]
		print("path text: ", pathText)
		var partModelTrianglesDictionary = responseDictionary["partModel"]
		var impingementData = responseDictionary["impingementData"]
		get_parent().get_node("PartViewObject/PartViewMesh").setTriangles(partModelTrianglesDictionary, impingementData)
		
	else:
		#Steven Edit
		#print("NewPath: ", newPath)
		#var typepath = typeof(newPath)
		#print(typepath)
		var PathSelection = {'Selection':String(newPath)}

		print(newPath)
		var responseJSON = get_node("/root/global").http_get_request("/sendSurfaceSelection", PathSelection)
		print(responseJSON)
		var responseDictionary = Dictionary()
		responseDictionary.parse_json(responseJSON)
		print(responseDictionary)
		pathText = responseDictionary["path"]
		print("path text: ", pathText)
		var partModelTrianglesDictionary = responseDictionary["partModel"]
		var impingementData = responseDictionary["impingementData"]
		get_parent().get_node("PartViewObject/PartViewMesh").setTriangles(partModelTrianglesDictionary, impingementData)
		#original
		#pathText = newPath
		#print("path text: ", pathText)
	clear()
		#var typepath = typeof(pathText)
		#print(typepath)
		
	var path = pathText
	numberOfPositions = path.size() / NUMBER_OF_ROWS_IN_PATH_DATA
	var pathDictionaryArray = dictionarify_path_array(path)
	populate_path_data_arrays(pathDictionaryArray)
	build_line()

func _ready():
	setNewPath("startup")

func get_length():
	return numberOfPositions

func build_line():
	self.begin(VS.PRIMITIVE_LINE_STRIP)
	for i in range(numberOfPositions):
		self.add_vertex(get_point_vector(i))
	self.end()

func populate_path_data_arrays(pathDictionaryArray):
	print ("path testing",pathDictionaryArray)
	midpointArray.clear()
	pointToArray.clear()
	lengthArray.clear()
	pointArray.clear()
	nozzleRotationArray.clear()
	timeArray.clear()
	for i in range(pathDictionaryArray.size() - 1):
		var index = i
		var pathDictionary = pathDictionaryArray[i]
		midpointArray.append(Vector3(pathDictionary["midpointX"], pathDictionary["midpointY"], pathDictionary["midpointZ"]) * PATH_SCALE)
		pointToArray.append(Vector3(pathDictionary["pointToX"], pathDictionary["pointToY"], pathDictionary["pointToZ"]) * PATH_SCALE)
		lengthArray.append(float(pathDictionary["length"]) * PATH_SCALE)
		pointArray.append(Vector3(pathDictionary["pointX"], pathDictionary["pointY"], pathDictionary["pointZ"]) * PATH_SCALE)
		nozzleRotationArray.append(Vector3(pathDictionary["nozzleRotationX"], pathDictionary["nozzleRotationY"], pathDictionary["nozzleRotationZ"]) * PATH_SCALE)
		timeArray.append(float(pathDictionary["time"]) * PATH_SCALE)
	var lastPointDictionary = pathDictionaryArray[pathDictionaryArray.size() - 1]
	pointArray.append(Vector3(lastPointDictionary["pointX"], lastPointDictionary["pointY"], lastPointDictionary["pointZ"]) * PATH_SCALE)

func get_point_vector(i):
	return pointArray[i]

func get_nozzle_rotation_vector(i):
	return nozzleRotationArray[i]

func get_length_at_point(i):
	return lengthArray[i]

func get_line_midpoint(i):
	return midpointArray[i]

func get_line_point_to_direction(i):
	return pointToArray[i]

func get_time(i):
	return timeArray[i]

func parse_path(text):
	var fullArray = []
	fullArray = text.split(",")
	
	#remove the brackets
	fullArray[0] = fullArray[0].substr(1, fullArray[0].length() - 1)
	fullArray[fullArray.size() - 1] = fullArray[fullArray.size() - 1].substr(0, fullArray[fullArray.size() - 1].length() - 2)
	
	return fullArray 

func dictionarify_path_array(pathArray):
	var pathDictionaryArray = []
	print("number of positions in path: ", numberOfPositions)
	for i in range(0, numberOfPositions):
		var pathDictionary = {}
		var index = i * NUMBER_OF_ROWS_IN_PATH_DATA
		pathDictionary["index"] = pathArray[index]
		pathDictionary["midpointX"] = pathArray[index + 1]
		pathDictionary["midpointY"] = pathArray[index + 3]
		pathDictionary["midpointZ"] = pathArray[index + 2]
		pathDictionary["nozzleRotationX"] = pathArray[index + 4]
		pathDictionary["nozzleRotationY"] = pathArray[index + 6]
		pathDictionary["nozzleRotationZ"] = pathArray[index + 5]
		pathDictionary["pointToX"] = pathArray[index + 7]
		pathDictionary["pointToY"] = pathArray[index + 9]
		pathDictionary["pointToZ"] = pathArray[index + 8]
		pathDictionary["length"] = pathArray[index + 10]
		pathDictionary["pointX"] = pathArray[index + 11]
		pathDictionary["pointY"] = pathArray[index + 13]
		pathDictionary["pointZ"] = pathArray[index + 12]
		pathDictionary["time"] = pathArray[index + 14]
		pathDictionaryArray.append(pathDictionary)
	var lastPointDictionary = {}
	lastPointDictionary["pointX"] = pathArray[(numberOfPositions - 1) * NUMBER_OF_ROWS_IN_PATH_DATA + 11]
	lastPointDictionary["pointY"] = pathArray[(numberOfPositions - 1) * NUMBER_OF_ROWS_IN_PATH_DATA + 13]
	lastPointDictionary["pointZ"] = pathArray[(numberOfPositions - 1) * NUMBER_OF_ROWS_IN_PATH_DATA + 12]
	pathDictionaryArray.append(lastPointDictionary)
	return pathDictionaryArray