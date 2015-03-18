from FactSetOnDemand import FactSetOnDemand, DataFrame, Factlet, UploadFactlet
import os
import time
import sys
try:
	# First, we get a handle to the FactSet OnDemand API.
	# This handle creation loads FactSet's DLL into memory
	factSetOnDemand = FactSetOnDemand.GetInstance()


	# In this example, we will run ExtractFormulaHistory and examine the unique
	# IDs and Dates in the returned data
	factlet = Factlet.ExtractFormulaHistory("xom,stl-no,fds,ibm,efc,appl,goog", "fg_eps(-1d,-1m,d)");
	
	# we can get a glimpse at the data being returned with getSummary. This is made for human reading, not for parsing.
	print factlet.getSummary() + "\n"
	
	# getUniqueId's gets us all the IDs returned.
	# In this example, we use this to group all the data by the ID it belongs to by creating a dict for each ID
	# Within each ID dict, we will group the data with the date
	uniqueIDs = factlet.getUniqueIDs();
	print "Printing list of unique IDs:\n"
	data = {}
	for i in xrange(len(uniqueIDs)):
		data[uniqueIDs[i]] = []
		print "\t" + uniqueIDs[i]

	#IMPORTANT
	#Here is where we can step through all of the data.
	for r in xrange(factlet.getNumberOfRows()):
		id = factlet.getValueAsString(0, r)		#we input column, row to take a single piece of data
		date = factlet.getValueAsString(1, r)
		fg_eps = factlet.getValueAsDouble(2, r)
		data[id].append((date, fg_eps))	# store both the date and fg_eps as a python tuple
	
	for id, dataPoints in data.items():
		print "Data for", id
		print dataPoints
		print "\n\n"
			
	
	factSetOnDemand = None
finally:
	FactSetOnDemand.CleanUp()
exit(0)