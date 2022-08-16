#!/usr/bin/env python

import pandas as pd

class CSV_Reader:
	"""This just reads the data from a CSV file and puts it into a dataframe
	Attributes:
		toolPathData: this is the dataframe
		getData(): reads the file specified below in the constructor

	"""

	def __init__(self):
		self.toolPathFile = "~/Desktop/RRAD_2016-17/gitRepository/gui/Backend/test.csv"
		self.toolPathData = {}

	def getData(self):
		self.toolPathData = pd.read_csv(self.toolPathFile, delimiter=',')
		return self.toolPathData

	def getPositionByAxis(self, i, axis):
		row = self.toolPathData.iloc[i];
		return row[axis]

	def getLength(self):
		return len(self.toolPathData.index)

	def makeItLookLikeSentFromPublisher(self):
		points = []
		for row in range(self.getLength()):
			for column in range(6):
				points.append(self.getPositionByAxis(row, column))
		path = points
		
		return path

