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

	translator = gapi.Translator(speech.lang, 'en-uk')
	cfileName = None
	try:
		engine = pyttsx.init()
		cfileName = psw.convert(fileName)
		print "processing the file: ", fileName
		
		flag = True
		if not listen:
			finger_prints = []
			finger_print_char = None
			for files in os.listdir(os.getcwd() + '/audio'):
				finger_print = acoustid.fingerprint_file('audio/' + files)
				finger_prints.append(finger_print[0])
				finger_print_char = finger_print[1]
				print files, finger_print

			current_fingerprint = acoustid.fingerprint_file(fileName)
			print "now recorded", current_fingerprint
			if current_fingerprint[0] > max(finger_prints) or current_fingerprint[0] < min(finger_prints) or current_fingerprint[1] != finger_print_char:
				flag = False

		if flag:
			phrase = speech.getText(cfileName)
			if phrase!=None:
				phrase = phrase.lower()
				if len(phrase.strip())>0:
					print 'text:',phrase
					# psw.play(speech.getAudio(phrase))
					if listen:
						listen = False
						if "weather" in phrase.lower():
							engine.say(get_weather())
							engine.runAndWait()
					if "ok jarvis" in phrase.lower() or "okay jarvis" in phrase.lower():
						if engine.isBusy():
							engine.say("yes sir?")
							engine.runAndWait()
							listen = True
	except Exception, e:
		import traceback
		traceback.print_exc()
		print "Unexpected error:", sys.exc_info()[0], e
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