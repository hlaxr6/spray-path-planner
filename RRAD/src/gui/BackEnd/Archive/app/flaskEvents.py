from app import app
from noThreadPathListener import PathListener
from threading import Event

@app.route('/getPath')
def getPath():
	pathPoints = PathListener()
	pathPoints.run()
	while pathPoints.complete is False:
		time.sleep(1)
	return str(pathPoints.getPath())

@app.route('/getLength')
def getLength():
	pathListener = PathListener()
	pathListener.run()
	while pathListener.complete is False:
		time.sleep(1)
	return str(pathPoints.getLength())