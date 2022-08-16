# Back End Documentation

## ---Overview---

Unless otherwise specified, the code in this package was written by Greg Harms. 

Everything in this package is written in Python, using Flask and ROS packages. The only script that should be executed to run the main application is "runFlaskServer.py". Everything else is a class used by that flask server.

Flask is a lightweight framework for Python used to create a web server. Even though this program is intended to run on one box, the simplicity of this tool makes it wonderful for acting as mediator between Godot and ROS.

Flask communicates with ROS with service classes that are run when it receives a HTTP request from Godot. Each time Godot needs to reach ROS for a new path or to submit modifications, it submits a request. This means Godot must initiate all communication with ROS, which shouldn't be a problem, as only the GUI should need to be event sensitive. If we need something to notify the GUI at any point, polling could easily be implemented. 



[TOC]



## ---API---

### runFlaskServer.py

This is the launcher file which simply runs a flask server. It imports the contents of the "app" folder, then executes the run() command to start the server. The app folder contains the init file, which sets up the Flask server by importing the flaskEvents.py file, where all of the events are handled. 





### app/flaskEvents.py

#### Description

This is where Flask's business logic lies. This file tells the Flask server what to do for each request it gets. It will then call the relevant ROS or file I/O classes to generate a response. When the user interface sends a request to Flask, this is the file that handles what to do with it.

**Inputs:** 

- HTTP post URL - The URL designates which function will be called. Each URL has it's own function to handle the response. 
- (Optional) JSON post content - This is used to pass data to the back end. So far, this has been used to send back path modifications and indexes of selected portions of the part or path. This information is formatted in [JSON](https://www.json.org/).

**Outputs:**

- Path - This may be an original path or updated path, depending on whether getPath is called under a startup condition or update condition. This is a dictionary, sent as JSON. This is how it is formatted:

```
path = [
	index, midpointX, midpointY, midpointZ, nozzleRotationX, nozzleRotationY, nozzleRotationZ, pointToX, pointToY, pointToZ, length, pointX, pointY, pointZ
]
```

- Part Model - When getPath is called, the part model is sent as well as the path. This is a dictionary, sent as JSON. This is how it is formatted:

```
triangles = {
	facet = {
		vertex1 = [
			x, y, z
		], vertex2 = [
			x, y, z
		], vertex3 = [
			x, y, z
		], normal
	}
}
```

- Impingement Data - Also only in getPath, the impingement data is sent along too. This is an array of values ranging from 0 to 1, each index represents a facet, ordered the same as the .stl file.

#### Member Functions

[getPath()](#getPath())

[pathModificaitons()](#pathModificaitons())

[sendSurfaceSelection()](#sendSurfaceSelection())

[getPartFacets()](#getPartFacets())

[getImpingementData()](#getImpingementData())

#### Member Function Descriptions

- ##### getPath()

This is the first call to be made when the user interface starts up. This will send the path, part model, and impingement data as a response. It gets its data by using modifications_client.py, TriangleListBuilder.py, and ImpingementModel.py.

- ##### pathModificaitons()

This is used to send modifications to ROS and receive a new path back. This may no longer be used in favor of sendSurfaceSelection() since we have simplified the amount of information needed to modify the path.

- ##### sendSurfaceSelection()

This is just like pathModifications(), but it should just receive a list of facet indexes that need more attention. 

- ##### getPartFacets(filepath)

Uses a file path to generate a dictionary of part model facets using the TriangleListBuilder class. This dictionary is used by GODOT to build an openGL mesh. In effect, this allows us to dynamically import a part model from a .stl file instead of using the editor to import a .obj. We could replace the TraingleListBuilder to allow for importing object in different file types without changing the front end if we need to.

- ##### getImpingementData(path, stlFilepath)

This just creates an ImpingementModel object and runs it to generate the data needed. Path is the generated tool path, which is not used right now (impingmentModel simply loads the PathPlan.csv). stlFilepath is the path to the part model .stl selected when the program starts.





### ImpingementModel.py

#### Description

This class was written by Braden to calculate coverage of the sprayer on the part model. 

**Inputs:**

- meshFile - string file path passed in when createImpingementData() is called. 


**Implicit Input:**

- PathPlan.csv - imported from a file, but the file changes every time the path planner runs.


**Output:**

- Facet_Value - array of impingement data. Array index corresponds with facet index.

##### 



### modifications_client.py

#### Description

This class is the ROS interface used to get a new path, either on startup or to generate a new path from some user modifications. 

**Inputs:**

- jsonMods - If the startup condition is true, this will just be a string containing "startup". If it is not, this will hold a JSON object with all of data needed by the ROS network to generate a new path.

**Outputs:**

- newPath - This is a JSON object of the format listed [above](#app/flaskEvents.py). The indexes run from start to finish.
- filepath - This is a string holding the path for the .stl part model.

#### Member Functions

[handle_modifications_client(self, jsonMods)](#handle_modifications_client(self, jsonMods))

[getPathArray(self, pathROSMessage)](#getPathArray(self, pathROSMessage))

#### Member Function Descriptions

- ##### handle_modifications_client(self, jsonMods)

Sends jsonMods to the ROS network. It then receives a file path to the .stl file and a tool path, which it then returns.

- ##### getPathArray(self, pathROSMessage)

Turns ROS formatted path into an array. 





### TriangleListBuilder.py

#### Description

Reads a .stl file and puts the data into a structure that can be easily transfered to Godot and then parsed into openGL. To use this, instantiate it passing in the .stl file path, then call getTriangles(). 

**Inputs:**

- filename - Part model .stl file path to be imported.

**Outputs:**

- triangles - Dictionary holding all part facets. It is structured like this:

```
triangles {
    triangle {
        vertex1 [
            x, y, z
        ], vertex2 [
            x, y, z
        ], vertex3 [
            x, y, z
        ], normal [
            x, y, z
        ]
    }
}
```

#### Member Functions

[makeTriangleList()](makeTriangleList())

[buildVertex(numpyArray)](buildVertex(numpyArray))

[buildTriangle(vertex1, vertex2, vertex3, normal)](buildTriangle(vertex1, vertex2, vertex3, normal))

[getTriangle()](getTriangle())

[zero()](zero())

[find_mins_maxs()](find_mins_maxs())

#### Member Function Descriptions

- ##### makeTriangleList()

Put each facet into the top dictionary, triangles. The key is the facet index.

- ##### buildVertex(numpyArray)

Take a numpy array and convert it into a python array so that it may be JSONified when it is transferred.

- ##### buildTriangle(vertex1, vertex2, vertex3, normal)

Use each vertex and facet normal to build the triangle dictionary.

- ##### getTriangle()

Returns the entire dictionary of triangles. This should be called by flask.

- ##### zero()

Puts the origin at the center of the part.

- ##### find_mins_maxs()

Finds the mins and maxes to be passed into the zero function.



