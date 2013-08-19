#/usr/bin/python
from obspy.neic import Client	# NEIC CWB Server Client for ObsPy
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.stream import read
from obspy.signal.invsim import evalresp
import warnings, glob, re, os, sys, string

# ----------------------------------------------
# Open cwb config file and read in lines
# 1) Station info
# 2) Date/time info for station
# 3) Duration of signal
# ----------------------------------------------
fin = open('station.cfg', 'r')
data = {}	# dict of cwb config data
data['station'] = []	# list for multiple stations 
for line in fin:
	if (line[0] != '#'):
		if line != '\n':
			newline = re.split('#', line)
			if "station" in newline[1]:
				data['station'].append(newline[0].strip())
			elif "date/time" in newline[1]:
				data['date/time'] = newline[0].strip()
			elif "duration" in newline[1]:
				data['duration'] = newline[0].strip()
			elif "ipaddress" in newline[1]:
				data['ipaddress'] = newline[0].strip()
			elif "httpport" in newline[1]:
				data['httpport'] = newline[0].strip()
			elif "filter" in newline[1]:
				data['filtertype'] = newline[0].strip()
			elif "bplower" in newline[1]:
				data['bplowerfreq'] = newline[0].strip()
			elif "bpupper" in newline[1]:
				data['bpupperfreq'] = newline[0].strip()
			elif "lp" in newline[1]:
				data['lpfreq'] = newline[0].strip()
			elif "hp" in newline[1]:
				data['hpfreq'] = newline[0].strip()
			elif "notch" in newline[1]:
				data['notch'] = newline[0].strip()

# ----------------------------------------------------------------
# Run cwb query to extract stream from server
# Jar file executable:
# java -jar CWBQuery.jar -s "IUANMO LHZ00" -b "2013/07/29 00:00:00" -d 3600 -t ms -o %N_%y_%j -hp
# java -jar CWBQuery.jar -s "IUANMO LHZ00" -b "2013/07/29 00:00:00" -d 3600 -t ms -o %N_%y_%j -h136.177.121.27
# ----------------------------------------------------------------
tmpUTC = data['date/time']
tmpUTC = tmpUTC.replace("/", "")
tmpUTC = tmpUTC.replace(" ", "_")

stationinfo = data['station']
datetimeUTC = str(tmpUTC)
datetimeQuery = str(data['date/time'])
duration = float(data['duration'])
ipaddress = str(data['ipaddress'])
httpport = int(data['httpport'])
filtertype = str(data['filtertype'])
if filtertype == "bandpass":
	bplowerfreq = float(data['bplowerfreq'])
	bpupperfreq = float(data['bpupperfreq'])
elif filtertype == "lowpass":
	lpfreq = float(data['lpfreq'])
elif filtertype == "highpass":
	hpfreq = float(data['hpfreq'])
elif filtertype == "notch":
	notch = float(data['notch'])
t = UTCDateTime(datetimeUTC)
'''print stationinfo
print datetimeUTC
print datetimeQuery
print duration
print ipaddress
print httpport
print t'''
#client = Client(host=ipaddr, port=httpport, timeout=30, debug=False)	# NEIC CWB Server Client
#print "NEIC Stream"
#st = client.getWaveformNSCL(stationinfo, t, duration)	# format agrees with CWBQuery.jar executable 

# ------------------------------------------------
# Pull specific station seed file using CWBQuery
# ------------------------------------------------
'''
print "\n"
files = glob.glob('/home/agonzales/Documents/ObsPy/examples/agonzales/SeedFiles/*')
for f in files:
	os.remove(f)	# remove temp seed files from SeedFiles dir
stationlen = len(stationinfo)
for i in range(stationlen):
	try:	
		os.system("java -jar /home/agonzales/Documents/ObsPy/examples/agonzales/CWBQuery/CWBQuery.jar -s " + '"'+stationinfo[i]+'"' + " -b " + '"'+datetimeQuery+'"'  + " -d " + '"'+str(duration)+'"' + " -t ms -o /home/agonzales/Documents/ObsPy/examples/agonzales/SeedFiles/%N_%y_%j -h " + '"'+ipaddress+'"') 
		print "\n"
	except socket.error as e:
		print traceback.format_exc()
		print "CWB QueryServer at " + self.host + "/" + str(self.port)
	except Exception as e:
		print traceback.format_exc()
		print "*****Exception found = " + str(e)
'''

# --------------------------------------------------------
# Open seed files from cwbQuery.py 
# Pull trace stats from data stream
# --------------------------------------------------------
'''
filelist = os.listdir(seedpath)
filelist = filter(lambda x: not os.path.isdir(x), filelist)
newest = max(filelist, key=lambda x: os.stat(x).st_mtime)
stream = read(newest)
print stream
'''
seedpath = "/home/agonzales/Documents/ObsPy/examples/agonzales/SeedFiles/"
os.chdir(seedpath)
filelist = sorted(os.listdir(seedpath), key=os.path.getctime)
filelen = len(filelist)
stream = [0 for x in range(filelen)]	# multidim streams list, streams for each file contain multiple traces so streams = [][] where the second entry denotes the trace index 
i = filelen-1
while i >= 0: 
	try:	
		stream[i] = read(filelist[i])	# read MSEED files from query
	except Exception as e:
		print "******Exception found = " + str(e)	
	i = i - 1

streamlen = len(stream)	# number of streams (i.e. stream files) 
trace = {}	# dict of traces for each stream
nfft = 0	# number of fft points, necessary for some filtering
for i in range(streamlen):
	strsel = stream[i]	
	tracelen = len(strsel)	# number of traces in stream
	index = str(i)	
	if tracelen == 1:	# single trace stream
		trace[index] = strsel[0]	# trace 0 in stream i
		nfft = trace[index].count()	
	else:			# multiple trace stream
		trace[index] = []	# list in dict 
		nfft = 0
		for j in range(tracelen):	
			trace[index].append(strsel[j])
			tr = trace[index] 	
			nfft = nfft + tr[j].count() 

# Loop through stream traces, if trace has sample rate = 0.0Hz 
# => NFFT = 0 then this trace will be removed
for i in range(streamlen):
	strsel = stream[i]
	tracelen = len(strsel)
	index = str(i)
	#print "Number of traces = " + str(tracelen)
	if tracelen == 1:
		#print "Station = " + str(trace[index].stats['station'])	
		if trace[index].stats['sampling_rate'] == 0.0:
			#print "removed trace[%d]" % i 
			strsel.remove(trace[index])	
		#print strsel 		
	else:
		#print "Station = " + str(trace[index][0].stats['station'])	
		for j in range(tracelen):	
			tr = trace[index]	
			if tr[j].stats['sampling_rate'] == 0.0:
				#print "removed trace[%d][%d]" % (i, j)	
				strsel.remove(tr[j])	
		#print strsel	

# ----------------------------------------------------------------
# Pull frequency response for station and run a simulation
# to deconvolve the signal
# ----------------------------------------------------------------
networkID = []
stationID = []
locationID = []
channelID = []
# Need stations listed in SeedFiles directory
for i in range(streamlen):
	tmpstation = filelist[i] 	
	stationindex = tmpstation.index('_')	
	networkID.append(str(tmpstation[0:2]))
	stationID.append(str(tmpstation[2:stationindex]))	
	locationindex = len(tmpstation)-11
	channelindex = len(tmpstation)-14
	locationID.append(str(tmpstation[locationindex:locationindex+2]))
	channelID.append(str(tmpstation[channelindex:channelindex+3]))

'''
for i in range(streamlen):
	print "networkID = " + networkID[i]	
	print "stationID = " + stationID[i]	
	print "locationID = " + locationID[i]
	print "channelID = " + channelID[i]
	print "\n"
'''

# ---------------------------------------------------------------------
# Loop through stations and get frequency responses for each stream
# ---------------------------------------------------------------------
# Pre-filter bandpass corner freqs
# eliminates end frequency spikes (H(t) = F(t)/G(t))
# G(t) != 0
c1 = 0.02
c3 = 0.05
c2 = c1
c4 = c3
resppath = "/home/agonzales/Documents/ObsPy/examples/agonzales/RESPS/"	
for i in range(streamlen):	
	# NOTE: Need a way to scp multiple files using station IDS
	# store resfilenames in a list. Alternate way is scp entire
	# response dir from aslres01
	# resppath = "/APPS/metadata/RESPS/"	# response filepath on aslres01
	resfilename = "RESP."+networkID[i]+"."+stationID[i]+"."+locationID[i]+"."+channelID[i]	# response filename
	resfile = resppath + resfilename
	os.chdir(resppath)
	cwd = os.getcwd()
	#os.system("scp agonzales@aslres01.cr.usgs.gov:" + resfile + " " + cwd)
	#resp = evalresp(1, nfft, resfilename, t, station=stationID, channel=channelID, network=networkID, locid=locationID, units="DIS", debug=False)
	resp = {'filename': resfilename, 'date': t, 'units': 'DIS'}

	# ------------------------------------------------------------------
	# Simulation/filter for deconvolution
	# NOTE: Filter will be chosen by user, this includes
	# filter coefficients and frequency ranges. Currently all stations	
	# run the same filter design, this will change depending on the 
	# network and data extracted from each station
	# ------------------------------------------------------------------	
	if filtertype == "bandpass":
		print "i = " + str(i)	
		print "station = " + str(filelist[i])	
		print "resp file = " + str(resfilename)	
		fl1 = bplowerfreq
		fl3 = bpupperfreq 
		fl2 = fl1
		fl4 = fl3 
		stream[i].simulate(paz_remove=None, pre_filt=(fl1, fl2, fl3, fl4), seedresp=resp, taper='True')	# deconvolution
		stream[i].filter(filtertype, freqmin=fl1, freqmax=fl3, corners=2)	# bandpass filter design
		print "\n"	
	elif filtertype == "lowpass":
		fl = lpfreq
		stream[i].simulate(paz_remove=None, pre_filt=(c1, c2, c3, c4), seedresp=resp, taper='True')	# deconvolution
		stream[i].filter(filtertype, freq=fl, corners=1)	# lowpass filter design 
	elif filtertype == "highpass":
		f1 = hpfreq
		stream[i].simulate(paz_remove=None, pre_filt=(c1, c2, c3, c4), seedresp=resp, taper='True')	# deconvolution
		stream[i].filter(filtertype, freq=f1, corners=1)	# highpass filter design	

'''
# ----------------------------------------------------------------
# Magnification (will also support user input)
# ----------------------------------------------------------------
mag = input("Enter magnification factor: ")
streamlen = len(stream)
if streamlen == 1:
	tr = 0	
	tr = stream[0]	# one trace	
	datalen = len(tr.data)	
	i = 0	
	for i in range(datalen):
		tr.data[i] = tr.data[i] * mag
else:
	tr = []	
	i = 0	
	for i in range(streamlen):
		datalen = len(tr[i].data)	
		for j in range(datalen):
			tr[i].data[j] = tr[i].data[j] * mag 

# ----------------------------------------------------------------
# Plot displacement data
# ----------------------------------------------------------------
stream.merge(method=1)
stream.plot(type='dayplot', interval=60, right_vertical_labels=False,
	number_of_ticks=7, one_tick_per_line=True, color=['k', 'r', 'b', 'g'],
	show_y_UTC_label=False) 
os.remove(resfilename)	# remove response file after computing response
'''
