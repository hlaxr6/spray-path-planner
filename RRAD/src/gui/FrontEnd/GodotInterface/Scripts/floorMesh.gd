extends MeshInstance

export(FixedMaterial)    var material    = null

func _ready():
	build_floor()

func build_floor():
	print ("No Floor")
	#var floorTool = SurfaceTool.new()
	#var mesh = Mesh.new()
	
	#floorTool.set_material(material)
	#floorTool.begin(VS.PRIMITIVE_TRIANGLE_STRIP)
	
	#floorTool.add_vertex(Vector3(500, -2, 500))
	#floorTool.add_vertex(Vector3(-500, -2, 500))
	#floorTool.add_vertex(Vector3(-500, -2, -500))
	#floorTool.add_vertex(Vector3(500, -2, 500))
	#floorTool.add_vertex(Vector3(500, -2, -500))
	#floorTool.add_vertex(Vector3(-500, -2, -500))
	
	##floorTool.generate_normals()
	#floorTool.index()
	
	#floorTool.commit(mesh)
	
	#self.set_mesh(mesh)