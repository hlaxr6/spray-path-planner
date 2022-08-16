#!/usr/bin/env python
import sys
from PyQt4 import uic, QtCore, QtGui
from Backend.add_markers import *
from Backend.RVizScheduler import *
from threading import Event

qtCreaterFile = "Frontend/PlayPauseRewind.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreaterFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		self.addMarkers = Add_Markers()
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)

		self.initializeArrowControls()

		self.buildRVizScheduler()

	def initializeArrowControls(self):
		self.arrowState = 'forward'
		self.playButton.clicked.connect(self.playArrow)
		self.pauseButton.clicked.connect(self.pauseArrow)
		self.rewindButton.clicked.connect(self.rewindArrow)
		self.arrowSlider.setMinimum(0)
		self.arrowSlider.setMaximum(self.addMarkers.getArrowDistance())
		self.arrowSlider.setSliderPosition(0)
		self.arrowSlider.valueChanged.connect(self.arrowSliderChanged)
		self.arrowSlider.sliderPressed.connect(self.arrowSliderPressed)


	def buildRVizScheduler(self):
		self.stopFlag = Event()
		self.rvizScheduler = RVizScheduler(self.stopFlag, self.addMarkers, self.arrowState, self.arrowSlider)
		self.rvizScheduler.daemon = True
		self.rvizScheduler.start()

	def arrowSliderPressed(self):
		self.stopFlag.set()
		self.pauseButton.setChecked(True)
		self.playButton.setChecked(False)
		self.rewindButton.setChecked(False)
		self.arrowState = 'slider'

	def arrowSliderChanged(self):
		if self.arrowState == 'slider':
		 	self.addMarkers.update('absolutePosition=' + str(self.arrowSlider.sliderPosition()))

	def playArrow(self):
		self.arrowState = 'forward'
		self.pauseButton.setChecked(False)
		self.rewindButton.setChecked(False)
		self.stopFlag.set()
		self.buildRVizScheduler()

	def pauseArrow(self):
		self.playButton.setChecked(False)
		self.rewindButton.setChecked(False)
		self.arrowState = 'stop'
		self.stopFlag.set()

	def rewindArrow(self):
		self.pauseButton.setChecked(False)
		self.playButton.setChecked(False)
		self.arrowState = 'reverse'
		self.stopFlag.set()
		self.buildRVizScheduler()

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MyApp()
	window.show()
	sys.exit(app.exec_())