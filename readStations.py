import os, re, string

# -------------------------------------------------------
# Open and read list of stations
# selected station will be put into cwb.cfg
# -------------------------------------------------------
fin = open('stationNames.txt', 'r')
stations = []	# list of stations
rmnetwork = ['AS', 'BF', 'BK', 'CD', 'DW', 'HG', 'SR', 'TS']	# removed networks
for line in fin:
		count = 0	
		# Remove all stations with rmnetwork key	
		# Every line can only have 1 occurrence within rmnetwork	
		for i in range(len(rmnetwork)):
			if line[0:2] == rmnetwork[i]:	
				count = count + 1	
				break	
		if count == 0:	
			line = line.replace("_", "")
			line = line.strip()	
			stations.append(line)	

# -------------------------------------------------------
# Pull desired station (will this be a user input?)
# If not then we can loop through all stations and print
# them to a config file (cwb.cfg)
# -------------------------------------------------------
# How will we know the start times for each station? 
# IU AFI:	start = 20:15 08/07/13
# CU CIP: 	start = 20:07 08/07/13
# IU FUNA:	start = 20:15 08/07/13 
# ------------------------------------------------------
stationlen = len(stations)

# Read in data from prestation.cfg this file contains
# channel/location, datetime/duration, etc.
fin = open('prestation.cfg', 'r')
for line in fin:
	if (line[0] != '#'):
		if line != '\n':
			newline = re.split('=', line)
			if "channel" in newline[0]:
				channelID = newline[1].strip()
			elif "locationID0" in newline[0]:
				locationID0 = newline[1].strip()
			elif "locationID1" in newline[0]:
				locationID1 = newline[1].strip()
			elif "datetime" in newline[0]:
				datetime = newline[1].strip()
			elif "duration" in newline[0]:
				duration = newline[1].strip()
			elif "ipaddress" in newline[0]:
				ipaddress = newline[1].strip()
			elif "httpport" in newline[0]:
				httpport = newline[1].strip()
			elif "filtertype" in newline[0]:
				filtertype = newline[1].strip()
			elif "bplower" in newline[0]:
				bplowerfreq = newline[1].strip()
			elif "bpupper" in newline[0]:
				bpupperfreq = newline[1].strip()
			elif "lpfreq" in newline[0]:
				lpfreq = newline[1].strip()
			elif "hpfreq" in newline[0]:
				hpfreq = newline[1].strip()
			elif "notchfreq" in newline[0]:
				notchfreq = newline[1].strip()

# Comments associated with each variable
stationcmt = "# station info"
datetimecmt = "# date/time info"
durationcmt = "# duration"
ipaddresscmt = "# ipaddress of local ANMO server"
httpportcmt = "# httpport number of local CWB Server (aslcwb.cr.usgs.gov) this will change accordingly to find open ports for ip addr run: nmap <ipaddr>"
filtertypecmt = "# filter type"
bplowerfreqcmt = "# bplower freq"
bpupperfreqcmt = "# bpupper freq"
lpfreqcmt = "# lp freq"
hpfreqcmt = "# hp freq"
notchfreqcmt = "# notch freq"
cfgcmt = "# Config file is populated by readStations.py\n# station info will be read from station list\n# execution times will depend on cronjob or an\n# external time file that lists times for each station\n# ---------------------------------------------------\n# These values should not be user input when running a cronjob\n# f1 = bandpass lowerbound\n# f3 = bandpass upperbound\n# mag = magnification factor\n# -------------------------------------------------\n"

stationlist = []
for i in range(stationlen):
	stringlen = len(stations[i])
	# Station IDs have a max size of 6, if (size < 6) then pad
	# station ID with (6-size+1) spaces
	if stringlen == 5:	
		tmp = stations[i] + "  " + channelID + locationID0 + "\t" + stationcmt
		stationlist.append(tmp)
	elif stringlen == 6: 
		tmp = stations[i] + " " + channelID + locationID0 + "\t" + stationcmt
		stationlist.append(tmp)

cfgout = open('station.cfg', 'w')
cfgout.write(cfgcmt)
cfgout.write("\n")
cfgout.write("# These variables will only change depending on the execution time and server used\n")
cfgout.write(datetime + "\t" + datetimecmt)
cfgout.write("\n")
cfgout.write(duration + "\t" + durationcmt)
cfgout.write("\n")
cfgout.write(ipaddress + "\t" + ipaddresscmt)
cfgout.write("\n")
cfgout.write(httpport + "\t" + httpportcmt)
cfgout.write("\n\n")

# Filter design for stations: this will change depending on how the
# user wants to filter the data and what station they're pulling the data
cfgout.write("# Filter Design\n")
if filtertype == "bandpass":
	fl1 = bplowerfreq	# lower band freq
	fl3 = bpupperfreq	# upper band freq
	cfgout.write(filtertype + "\t" + filtertypecmt + "\n")
	cfgout.write(fl1 + "\t" + bplowerfreqcmt + "\n")
	cfgout.write(fl3 + "\t" + bpupperfreqcmt + "\n\n")
elif filtertype == "lowpass":
	lpfl = lpfreq	# corner freq (this value will change depending on data)
	cfgout.write(filtertype + "\t" + filtertypecmt + "\n")
	cfgout.write(lpfl + "\t" + lpfreqcmt + "\n\n")
elif filtertype == "highpass":
	hpfl = hpfreq	# corner freq (this value will change depending on data)
	cfgout.write(filtertype + "\t" + filtertypecmt + "\n")
	cfgout.write(hpfl + "\t" + hpfreqcmt + "\n\n")	
elif filtertype == "notch":
	notchfl = notchfreq
	cfgout.write(filtertype + "\t" + filtertypecmt + "\n")
	cfgout.write(notchfl + "\t" + notchfreqcmt + "\n\n")

# Print station info to config file
for i in range(len(stationlist)):
	cfgout.write(stationlist[i] + "\n")






