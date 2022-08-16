# RRAD Catkin Workspace Overview

## Installation:

clone from this repository with ```git clone https://git.uark.edu/Automation_Lab/RRAD.git

git tutorial at https://www.atlassian.com/git/tutorials

##### Dependencies:

To install [Python](https://www.python.org/), open a console window and type:

```bash
sudo apt update
sudo apt dist-upgrade
sudo apt install python2.7 python-pip
sudo apt install python3-pip
```



Then, to install [Flask](http://flask.pocoo.org/) type:

```bash
pip install Flask
```



To install [ROS](http://www.ros.org/), follow the instructions [here](http://wiki.ros.org/kinetic/Installation/Ubuntu). To get familiar with the software, their [tutorials](http://wiki.ros.org/ROS/Tutorials) are very helpful. To make sure that your setup.bash file is sourced every time you open a console window, you may add it to your .bashrc file. You may add it by opening a command prompt with ctrl+alt+t and type:

```bash
echo "source ~/[catkin_ws]/devel/setup.bash" >> ~/.bashrc
```

Replace [catkin_ws] with the name of your catkin base directory. You may also just open the .bashrc file in a text editor and add the command to the end of the document.



At least one absolute file path must be changed in this project folder. I have attempted to scrub most of them, but due to continued changes, you may see more show up as errors when you run the program. The one that must always be changed is in [launchBackEnd.bash](./src/gui_launch/launchBackEnd.bash). Open the file in your favorite text editor and replace the string in the variable "CATKIN_WORKSPACE" with the path to your top catkin directory.



##### Editing code:

Use whichever text editor you prefer for the Python code and makefiles. For Godot code, the editor is located in the gui/FrontEnd folder. 



## Running it:

1. To launch the ROS nodes and Flask server, first, make sure that you source your catkin_workspace/devel/setup.bash if you have not already added it to your .bashrc file.  

2. Make sure that all of the files to be executed have permission to execute. 

3. From a command line, type:

   ```bash
   rosrun gui_launch launchBackEnd.bash
   ```

   This will launch the roscore, flask server, and all of the ROS nodes.

4. To launch the user interface, either run an executable exported from the GODOT editor or launch the GODOT editor and run it from there by opening the project, then clicking the play button at the top of the editor window.



## Packages:

Each package has more specific documentation in its folder. Relative links are provided in this document for ease of access. Just follow the link in the package heading below! 



#### gui:

This package contains both the front end ([GODOT](https://godotengine.org/)) and back end (Python/Flask) portions of the user interface. The front end uses the back end to communicate with ROS and the computer's file system. 

##### 	[FrontEnd](./src/gui/FrontEnd/FrontEndDocumentation.md):

This code is written in GDScript, which is much like Python, using the [GODOT](https://godotengine.org/) open source game engine, version 2.1.4. 

Godot is used in order to easily generate 3D objects and UI tools such as buttons and sliders. The engine also handles collision detection, which is used for clicking on objects in the visual field. The engine is built on OpenGL, and in fact, you can write OpenGL code to generate geometry programmatically within the editor instead of importing a model from a file. Since the Godot project is open source, if you find anything that is not available through the editor, you may create a package in C++ to extend the engine to meet your needs. I thought this program was simple enough to use to make coding a new feature quick and easy, but also flexible enough to allow us to do whatever we need.

Godot only accepts .obj mesh files, which you may export from [blender](https://www.blender.org/) or [Tinkercad](https://www.tinkercad.com/). I have also built a .stl file importer so we don't have to convert the file between path building and displaying in the gui. This process is more clearly defined in the front end documentation. 

Godot does not need to be installed to work. It can even be run from a flash drive if you want.

You may start the GODOT editor by starting the program in the FrontEnd folder. The project files are located in  GodotInterface. To open the project in the editor, launch the editor, then import the project head at FrontEnd/GodotInterface/engine.cfg. The files are better organized in Godot's interface than in the file system, so go ahead and launch the editor to do anything with that code. 

##### 	[BackEnd](./src/gui/BackEnd/BackEndDocumentation.md):

This code is written in [Python](https://www.python.org/) 2.7.12 and [Flask](http://flask.pocoo.org/) 0.12.2.

Flask is a lightweight framework for Python used to create a web server. Even though this program is intended to run on one box, the simplicity of this tool makes it wonderful for acting as mediator between Godot and ROS.

Flask communicates with ROS with service classes that are run when it receives a HTTP request from Godot. Each time Godot needs to reach ROS for a new path or to submit modifications, it submits a request. This means Godot must initiate all communication with ROS, which shouldn't be a problem, as only the GUI should need to be event sensitive. If we need something to notify the GUI at any point, polling could easily be implemented. 

The Flask server's executable is called runFlaskServer.py. The other files in this directory are classes used to perform different functions listed in the back end documentation. The app folder contains the init file required by Flask, as well as flaskEvents.py, which handles all requests thrown at Flask. 



#### [gui_launch](./src/gui_launch/guiLaunchDocumentation.md):

This package was initially meant to house a ROS launch file, but after researching how they work, I ended up going with a bash launch script instead. This allows for launching non-ROS executables, such as the Flask server and roscore itself. If later it becomes easier to make the Flask server and Godot export into a ROS runnable program, that is still possible. 

The script has a variable that must be changed to run on a different computer. The CATKIN_WORKSPACE variable must contain the path to **your** catkin workspace.

The bash script can called if the devel/setup.bash file is first sourced using this command:

```
rosrun gui_launch launchBackEnd.bash
```



#### rrad_wash_cell:

Need to work on this once Steven finishes updating his algorithms.



#### [ur](./src/ur/README.md):

This package contains the tools for simulating and controlling a UR robot. We may have to switch this out to use a different type of robot. Not sure if this is needed still.

This was mostly used by Rahul for simulating the path in RViz.



This file was created by Greg Harms using [Typora](https://typora.io/). Email with any questions or comments at greg@plotsandschemes.com*