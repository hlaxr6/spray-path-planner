from __future__ import print_function
from app import app
from csv_reader import CSV_Reader 
from flask import Flask, request
import sys

@app.route('/getPath')
def getPath():
	csvFile = request.args.get('path')
	print("file = " + csvFile, sys.stdout)
	reader = CSV_Reader(csvFile)
	print("data = " + str(reader.getData()), sys.stdout)
	reader.getData
	return str(reader.makeItLookLikeSentFromPublisher())


@app.route('/getLength')
def getLength():
	csvFile = request.args.get('path')
	reader = CSV_Reader(csvFile)
	return str(reader.getLength())