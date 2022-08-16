# Front End Documentation

## --Overview--

This section was written by Greg Harms

This is all written in gdscript using the Godot's game engine IDE, the launcher of which can be located in the FrontEnd folder. The version used was Godot Engine v2.1.4.stable.official. Documentation for this language and engine can be found [here](http://docs.godotengine.org/en/3.0/classes/). 

This code was written before the new version (3.0) of Godot, which probably provides some features to make life easier in the future. If you find a reason to switch versions, the engine provides a way to convert your code by opening the project in the IDE and clicking Tools -> Export to Godot 3.0 (WIP). 

The FrontEnd folder contains an Archive folder which contains old code from when we were expecting to build the UI using Python, QT, and RViz. This is no longer used at all and may not be useful. The Some Exports folder, also in the FrontEnd folder contains a few different exports from Godot which reflect old versions of this project. I don't expect these to be super useful to anyone unfamiliar with them, so I will neglect to document their purposes. 

The Godot project files are located in FrontEnd/GodotInterface.  The project is imported by opening the .cfg file, engine.cfg. The Images folder contains all 2D images required by the project, Materials folder contains the textures used to cover the models, and the Models folder contains the 3D models that have been imported into the project from .obj files. Godot only accepts .obj files to import.

This document will focus on the Scripts folder and the node hierarchy within Godot, whether or not a script is attached. I have mainly used the node tree in the Godot IDE to navigate the scripts files, so my organization lies in there rather than in a file tree. 





[TOC]



## ---API---

### global.gd

This is a root level script that is not attached to any node. You may access this by using the function *get_node("/root/global")*. Currently, this is just used as an easy way to get to the http_get_request function.

#### Member Functions

[http_get_request(request, dictionaryPayload)](#http_get_request(request, dictionaryPayload))

#### Member Function Descriptions

- ##### http_get_request(request, dictionaryPayload)

Uses HTTP POST to make a request to the Flask server.  The request argument may be /getPath, /pathModifications, or /sendSurfaceSelection as defined by the flaskEvents.py file in the BackEnd folder. The dictionaryPayload argument is converted to JSON to send to flask as a payload. Send "" if you don't need a payload, such as in the startup condition of the /getPath request.





### FloorMesh

This is attached to the floorMesh.gd script. 

This node uses the Godot build-in OpenGL functions to create a plane that serves as the floor. You can set the material from the Godot inspector because the script exports that variable to the editor. 

#### Member Functions

[build_floor()](#build_floor())

#### Member Function Descriptions

- ##### build_floor()

This function, called when the program starts with _ready(), just generates the floor mesh using a material set in the Godot Inspector tab.





### PartViewObject

This node is attached to the partViewArea.gd script.

This is a RigidBody which handles all of the collision and selection of part facets.

#### Member Variables

selectedTriangles - Array that holds the indexes of each selected facet.

dragging - Boolean that is set when the left mouse button is held down.

mousPos - Position where a ray cast from the mouse contacts the part in global coordinates.

surfaceSelectSelected - Whether or not the Surface Select toolbar button has been pressed.

removeSelected - Whether or not the remove button has been pressed.

cursorWidth - updated by the cursorWidth slider. 

#### Member Functions

[_process(delta)](#_process(delta))

[checkIfContiguousInRange(triangles, triangle, selection, surfaceClick)](#checkIfContiguousInRange(triangles, triangle, selection, surfaceClick))

[isWithinBrushWidth(surfaceClick, possibleTriangle)](#isWithinBrushWidth(surfaceClick, possibleTriangle))

[isEdge(possibleTriangle, currentTriangle)](#isEdge(possibleTriangle, currentTriangle))

[getClosestTriangle(triangles, surfaceClick)](#getClosestTriangle(triangles, surfaceClick))

[isOnPlane(triangle, surfaceClick)](#isOnPlane(triangle, surfaceClick))

[addShapes(mesh)](#addShapes(mesh))

[_on_PartViewObject_input_event( camera, event, click_pos, click_normal, shape_idx )](#_on_PartViewObject_input_event( camera, event, click_pos, click_normal, shape_idx ))

[setSurfaceSelectSelected(selected)](#setSurfaceSelectSelected(selected))

[setRemoveSelected(selected)](#setRemoveSelected(selected))

[clearAllSelected()](#clearAllSelected())

[getSelectedTrianglesIndexes()](#getSelectedTrianglesIndexes())

#### Member Function Descriptions

- ##### _process(delta)

Handles mouse input. First it checks which facets of the mesh are being clicked on, spreads the selection to the appropriate range, and calls the refresh function in the mesh object to color the selection. Also removes the selection if the remove button is toggled. 

- ##### checkIfContiguousInRange(triangles, triangle, selection, surfaceClick)

This checks to see if each facet is connected to the clicked facet and within the selection area.

- ##### isWithinBrushWidth(surfaceClick, possibleTriangle)

Checks that facet is within the area of selection, determined by the brush width.

- ##### isEdge(possibleTriangle, currentTriangle)

If the angle of the normals of the two triangles is greater than pi/6, this returns true.

- ##### getClosestTriangle(triangles, surfaceClick)

Finds the closest facet to the cursor click projected onto the surface of the part mesh.

- ##### isOnPlane(triangle, surfaceClick)

Checks if the triangle is on a plane with the surface click. This is used to exclude facets whos centers are closest to the click, but not the actual facet.

- ##### addShapes(mesh)

Creates a trimesh shape from the passed in mesh and adds it to the PartViewObject

- ##### _on_PartViewObject_input_event( camera, event, click_pos, click_normal, shape_idx )

Sets and unsets the dragging boolean.

- ##### setSurfaceSelectSelected(selected)

Sets the surfaceSelectSelected boolean.

- ##### setRemoveSelected(selected)

Sets the removeSelected boolean.

- ##### clearAllSelected()

Removes everything from the selectedTriangles array.

- ##### getSelectedTrianglesIndexes()

Returns the selectedTriangles array.





### PartViewMesh

This is attached to the partView.gd script. 

This is a MeshInstance which builds a mesh out of the .stl file sent to Godot through Flask. Color is also set through this node, for impingement data or dynamically updating to show selection.

#### Member Variables

SCALE - Constant variable to convert the mesh to the same scale as the path. This should probably be set dynamically when we figure out how big the real parts will be. 

triangles - Array of facets received from Flask

surfTool - SurfaceTool used to instantiate a programmatically generated mesh. 

#### Member Functions

[setTriangles(newTriangles, impingementData)](#setTriangles(newTriangles, impingementData))

[refreshMesh(selectedTriangles)](#refreshMesh(selectedTriangles))

[changeColor(triangle, selectedTriangles)](#changeColor(triangle, selectedTriangles))

[vectorizePointArrays(triangles, impingementData)](#vectorizePointArrays(triangles, impingementData))

[makeDummyColorValue(triangle)](#makeDummyColorValue(triangle))

[buildVector(array)](#buildVector(array))

[resize(triangles)](#resize(triangles))

[impingementValueToColor(value)](#impingementValueToColor(value))

[monochromeImpingementValueToColor(value)](#monochromeImpingementValueToColor(value))

#### Member Function Descriptions

- ##### setTriangles(newTriangles, impingementData)

  Used on startup to generate the mesh. This is called from Path after receiving data from Flask.

- ##### refreshMesh(selectedTriangles)

  Used to refresh the color of the facets. Called from PartViewObject when a facet is selected.

- ##### changeColor(triangle, selectedTriangles)vectorizePointArrays(triangles, impingementData)

  If the triangle is in the array of selected triangles, color it purple. Otherwise use the color defined in the triangle dictionary.

- ##### makeDummyColorValue(triangle)

  This was used to create false impingement data for display purposes. This may be useful to test various things later. 

- ##### buildVector(array)

  Turn an array of three values into a vector object which may be used to build the mesh.

- ##### resize(triangles)

  Use the SCALE variable to change adjust the size of the mesh.

- ##### impingementValueToColor(value)

  Convert the 0 - 1 impingement intensity to heat map colors.

- ##### monochromeImpingementValueToColor(value)

  Useful to reduce the noise of the tricolor heat map. Use instead of the standard impingementValueToColor method. 





### Path

This is attached to the path.gd script. 

This node imports the path, part model, and impingement data all at once from Flask, then displays the path using ImmediateGeometry (Godot's OpenGL interface).

#### Member Variables

NUMBER_OF_ROWS_IN_PATH_DATA - Constant used to keep track of how many attributes are in the path ROS message. This should probably be columns instead of rows.

PATH_SCALE - Constant variable to convert the mesh to the same scale as the part mesh. This should probably be set dynamically when we figure out how big the real parts will be. 

midPointArray - An array of vectors each of which define the midpoint of the line segment between two path nodes.

pointToArray - An array of vectors that shows where the line segment should point to in order to reach the next node from the midpoint. 

lengthArray - An array that shows the length of the line segment between two nodes.

pointArray - An array of vectors that defines where each node of the path lies.

nozzleRotationArray - An array of vectors that shows where the nozzle will be pointing at each node of the path.

numberOfPositions - This is how many positions are in the path plan. 

#### Member Functions

[setNewPath(newPath)](#setNewPath(newPath))

[build_line()](#build_line())

[populate_path_data_arrays(pathDictionaryArray)](#populate_path_data_arrays(pathDictionaryArray))

[parse_path(text)](#parse_path(text))

[dictionarify_path_array(pathArray)](#dictionarify_path_array(pathArray))

#### Member Function Descriptions

- ##### setNewPath(newPath)

  If newPath is "startup", this queries the Flask server for the initial path data, impingement data and part model data, and then it sends the impingement data and part model to the PartViewMesh object. If it is not "startup", it clears the current path nodes. In both cases, it calls functions to parse the path string into arrays and build the line on screen.


- ##### build_line()

  Use ImmediateGeometry to create the line on screen.


- ##### populate_path_data_arrays(pathDictionaryArray)

  Use a dictionary of path points to populate the appropriate arrays. Each index corresponds to the same point.

- ##### parse_path(text)

  Parse a path string into an array, returns that.

- ##### dictionarify_path_array(pathArray)

  Turns path array into a dictionary. If the data types change, this must change. Would prefer to pass in JSON from Flask in the future to skip this whole process. 







### Nozzle

This is attached to the nozzle.gd script. 

Displays a nozzle object on the screen and controls its movement to reflect where the sprayer tool will be at any point along the tool path. 

#### Member Functions

[_process(delta)](#_process(delta))

[increment_delta(delta, pathNode)](#increment_delta(delta, pathNode))

[get_active_point()](#get_active_point())

[set_position_from_slider(activePointPassed, deltaPassed)](#set_position_from_slider(activePointPassed, deltaPassed))

[set_move_forward()](#set_move_forward())

[set_move_backward()](#set_move_backward())

[set_stop_moving()](#set_stop_moving())

[set_position(currentPoint, nextPoint)](#set_position(currentPoint, nextPoint))

[set_look_at(currentPoint)](#set_look_at(currentPoint))

#### Member Function Descriptions

- ##### _process(delta)

  Called every delta seconds. Sets nozzle position.

- #####increment_delta(delta, pathNode)

  Keeps track of the distance traveled by the nozzle based on moving direction and delta.

- #####get_active_point()

  Returns the point which the nozzle is at or has just passed.

- #####set_position_from_slider(activePointPassed, deltaPassed)

  Sets the position along the path to position assigned by the slider.

- #####set_move_forward()

  Sets the direction to forward

- #####set_move_backward()

  Sets the direction to backward

- #####set_stop_moving()

  Sets the speed to stopped.

- #####set_position(currentPoint, nextPoint)

  Tells the nozzle where to be at any given point.

- #####set_look_at(currentPoint)

  Tells the nozzle where to point.





### Spray

This is a simple transparent mesh to show the user approximately where the spray will land on the part.





### PlayPauseRewindBox

This is attached to the PlayPauseRewindBox.gd script. 

Interface for setting each of the nozzle movement buttons. Since hitting rewind should unset play, this is here to make these sorts of functions more natural feeling. 

#### Member Functions

[set_move_forward()](#set_move_forward())

[set_move_stopped()](#set_move_stopped())

[set_move_backward()](#set_move_backward())

#### Member Function Descriptions

- #####set_move_forward() 

  Sets the nozzle to start moving forward and adjusts the color of the buttons to reflect the choice.

- #####set_move_stopped()

  Sets the nozzle to stop moving and adjusts the color of the buttons to reflect the choice.

- #####set_move_backward()

  Sets the nozzle to start moving backward and adjusts the color of the buttons to reflect the choice.





### RewindButton

This is attached to the rewindButton.gd script. 

Simply calls the related function in the PlayPauseRewindBox.

#### Member Functions

_on_RewindButton_toggled( pressed )





### PlayPauseButton

This is attached to the playButton.gd script. 

Simply calls the related function in the PlayPauseRewindBox.

#### Member Functions

_on_PlayPauseButton_toggled( pressed )





### NozzleSlider

This is attached to the nozzleSlider.gd script. 

This slider allows the user to jump to whichever position along the path they like. It also updates to show how far along the path it is.

#### Member Functions

[_process(delta)](#_process(delta))

[_on_NozzleSlider_input_event( ev )](#_on_NozzleSlider_input_event( ev ))

#### Member Function Descriptions

- #####_process(delta) 

  If it is not being adjusted, this sets the value held in the slider to the relative position of the nozzle along the path.

- #####_on_NozzleSlider_input_event( ev )

  Click listener that sets the value of the slider and calls the set position function in the nozzle object if it is moved.





### RotationPitch

This is attached to the cameraMovement.gd script. 

Separating the pitch and yaw gives the user much more natural feeling camera movement around a central point. All of the camera functions are in this node, including setting to the predefined front, top and isometric views.

#### Member Functions

[_input(event)](#_input(event))

[set_camera_front()](#set_camera_front())

[set_camera_top()](#set_camera_top())

[set_camera_isometric()](#set_camera_isometric())

#### Member Function Descriptions

- ##### _input(event)

  Event listener to handle mouse dragging. Sets position of the camera relative to the movement. 

- #####set_camera_front()

  Sets camera to preset front view position.

- #####set_camera_top()

  Sets camera to preset top view position.

- #####set_camera_isometric()

  Sets camera to preset isometric view position.





### RotationYaw

Another node to separate the two types of movement. Allows for more natural movement.





### Camera

Camera node attached to the two movement nodes. May be moved in and out from the center. Also has a light attached to it so that it always points directly onto the part. This may flood too much light in to see smaller indentions, so remove it if more complex parts are harder to see.





### ToolBar

This is attached to the toolBar.gd script. 

Handles signals from FrontView, TopView, and IsometricView buttons. These just call a function in the cameraMovement.gd script.

#### Member Functions

[_on_FrontView_pressed()](#_on_FrontView_pressed())

[_on_TopView_pressed()](#_on_TopView_pressed())

[_on_IsometricView_pressed()](#_on_IsometricView_pressed())

#### Member Function Descriptions

- ##### _on_FrontView_pressed()

  Listens for the button press and calls the corresponding method in the cameraMovement script.

- #####_on_TopView_pressed()

  Listens for the button press and calls the corresponding method in the cameraMovement script.

- #####_on_IsometricView_pressed()

  Listens for the button press and calls the corresponding method in the cameraMovement script.





### SelectSurfaceButton

This is attached to the selectSurfaceButton.gd script. 

Turns on the ability to select surfaces and reveals the surface selection tools. This may be unnecessary if there remain to be so few things to do with the program. May remove to keep it more simple.

#### Member Functions

[_on_SelectSurfaceButton_toggled( pressed )](#_on_SelectSurfaceButton_toggled( pressed ))

#### Member Function Descriptions

- ##### _on_SelectSurfaceButton_toggled( pressed )

  Activates surface selection functionality and displays extra controls for manipulating the selection.





### SurfaceSelectControls

This is attached to the surfaceSelectControls.gd script. 

Tools for controlling the surface selection. Allows the user to remove individual facets by clicking remove, then clicking on the selected facets, clear all selected facets, change the width of the selection brush, or submit the facets to ROS.

#### Member Functions

[_ready()](#_ready())

[_on_RemoveButton_toggled( pressed )](#_on_RemoveButton_toggled( pressed ))

[_on_ClearAllButton_pressed()](#_on_ClearAllButton_pressed())

[_on_BrushWidthButton_toggled( pressed )](#_on_BrushWidthButton_toggled( pressed ))

[_on_BrushWidthSlider_value_changed( value )](#_on_BrushWidthSlider_value_changed( value ))

[_on_SubmitSelectionButton_pressed()](#_on_SubmitSelectionButton_pressed())

[changeCursorToPointer()](#changeCursorToPointer())

[changeCursorToSelectionCursor()](#changeCursorToSelectionCursor())

#### Member Function Descriptions

- ##### _ready()

  Preload the texture that the cursor switches to.

- #####_on_RemoveButton_toggled( pressed )

  Sets the PartViewObject to switch to removing selection rather than adding.

- #####_on_ClearAllButton_pressed()

  Clears all selected facets.

- #####_on_BrushWidthButton_toggled( pressed )

  Toggles the slider used to adjust the brush width.

- #####_on_BrushWidthSlider_value_changed( value )

  Adjusts the brush width texture and sends the size to the PartViewObject to determine how wide the selection radius should be. 

- #####_on_SubmitSelectionButton_pressed()

  When this is hooked up, it should send the contents of PartViewObject's selectedTriangles to Flask.

- #####changeCursorToPointer()

  Sets the cursor back to a pointer.

- #####changeCursorToSelectionCursor()

  Sets the cursor to the new texture.





### FrontView

Moves the camera to the front of the part.





### TopView

Moves the camera to the top of the part.



### IsometricView

Moves the camera to an isometric view of the part.