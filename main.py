import sys
import numpy as np
import psw
import gapi

import pyttsx
import os
speech = gapi.Speech('en-uk')


import requests
import json
import acoustid

def get_ip_address():
    r = requests.get("http://ipinfo.io/ip")
    return r.content.replace("\n", "")

def get_location():
	r = requests.get("http://ip-api.com/json/" + get_ip_address())
	data = json.loads(r.content)
	return data.get('lat'), data.get('lon')

def get_weather():
	lat, lon = get_location()
	r = requests.get("http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s" % (str(lat), str(lon)))
	data = json.loads(r.content)
	return data.get("weather")[0].get("description") + " sir, with temperature of " + str(int(data.get("main").get("temp")) - 272.15) + " degree Celsius."

def handler(fileName):
	global speech, listen

	cfileName = None
	try:
		engine = pyttsx.init()
		cfileName = psw.convert(fileName)
		print "processing the file: ", fileName
		
		flag = True
		if not listen:
			with open('jarvis_fingerprints_samples', 'r') as f:
				fingerprints_json = json.loads("".join(f.readlines())).get("data")
				finger_prints = fingerprints_json.get("vals")
				finger_print_char = fingerprints_json.get("char")

			current_fingerprint = acoustid.fingerprint_file(fileName)
			print "now recorded", current_fingerprint
			if current_fingerprint[0] > max(finger_prints) or current_fingerprint[0] < min(finger_prints) or current_fingerprint[1] != finger_print_char:
				flag = False

		if flag:
			phrase = speech.getText(cfileName)
			if phrase!=None:
				phrase = phrase.lower()
				if len(phrase.strip())>0:
					print 'text:', phrase
					if listen:
						listen = False
						if "weather" in phrase.lower():
							engine.say(get_weather())
							engine.runAndWait()
					if "jarvis" in phrase.lower():
						print "got in"
						print engine.isBusy()
						if engine.isBusy():
							engine.say("yes sir?")
							engine.runAndWait()
							listen = True
	except Exception, e:
		import traceback
		traceback.print_exc()
		listen = False
		print "Unexpected error:", sys.exc_info()[0], e
		engine.say("I didn't catch that, sir.")
		engine.runAndWait()
	finally:
		print "in finally"
		for fl in os.listdir(os.getcwd()):
			__, ext = os.path.splitext(fl)
			if ext == '.mp3' or ext == '.flac' or ext == '.wav':
				os.remove(fl)
	return True


mic = psw.Microphone()
print 'initializing...'
sample = np.array(mic.sample(200))
print 'done'
listen = False
mic.listen(handler, sample.mean(), sample.std())