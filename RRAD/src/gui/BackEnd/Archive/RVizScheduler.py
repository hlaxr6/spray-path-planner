import time
from threading import Thread
from add_markers import Add_Markers

class RVizScheduler(Thread):
## pass an Event() into the event arguement to stop this thread. Ex, if passed in stopFlag = Event(), 
## the thread will stop when stopFlag.set() is called from the code that started the thread

	def __init__(self, event, addMarkersPassed, statePassed, arrowSliderPassed):
		Thread.__init__(self)
		self.stopped = event
		self.addMarkers = addMarkersPassed
		self.state = statePassed
		self.arrowSlider = arrowSliderPassed

	def run(self):
		while not self.stopped.wait(0.1):
			self.addMarkers.update(self.state)
			self.arrowSlider.setSliderPosition(self.addMarkers.getArrowSingleNumberPosition())
