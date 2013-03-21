#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import sys
import os
import subprocess

def init_raspy():
	print "Initialize ..."
	
	print "Set I/O Pins."

	# to use Raspberry Pi board pin numbers
	GPIO.setmode(GPIO.BOARD)

	# set up GPIO input channel with pull-up control
	# (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
	GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	print "Define global variables."

	END_ROTARY = False 
	HOOK = False
	RI = False
	number_length = 0

	print "Initialize SIP client."
	os.system("linphonecsh init")
	print "Register SIP client."
	con_check()
	print "Register SIP client success."

def con_check():
	os.system('linphonecsh unregister')
	time.sleep(0.5)
	os.system("linphonecsh register --host my.voip-provider.com --username myUserName --password SWORDFISH")
	time.sleep(0.5)
	s = os.popen('linphonecsh status register')
	check = s.read()
	
	if check == "registered=-1\n" or check == "registered=0\n" or check == "registered=0" or check == "registered=-1" or check == "" or check == "\n":
		while check == "registered=-1\n" or check == "registered=0\n" or check == "registered=0" or check == "registered=-1" or check == "" or check == "\n":
			os.system("linphonecsh register --host my.voip-provider.com --username myUserName --password SWORDFISH")
			time.sleep(0.5)	
			s = os.popen('linphonecsh status register')
			check = s.read() 
			print check
	
def incoming_call():
	# Dial Fake-Number to check, wether call is running
	s = os.popen('linphonecsh status hook')
	output = s.read()
	check = output.find("Incoming call", 0) 
	if check != -1:
		print "Incoming call."
		HOOK = GPIO.input(13)

		# Check whether hook is off
		if HOOK == False:
			# Answer the call
			os.system("linphonecsh generic answer")	

			HOOK = GPIO.input(13)
			while HOOK == False:
				HOOK = GPIO.input(13)
		
			# Hangup
			print "User has hung up."
			os.system("linphonecsh hangup")

def place_call():

	TIME_OUT = False
	dialed_number = 0
	number_length = 0
	tel_str = ""

	print "Phone is off Hook! Dial: "

	while TIME_OUT == False:

		input_value_new = GPIO.input(11)
		END_ROTARY = GPIO.input(12)
		HOOK = GPIO.input(13)
	
		while END_ROTARY == False and HOOK == False: #noch zu pruefen 

			END_ROTARY = GPIO.input(12)
			HOOK = GPIO.input(13)
			while input_value_new == True:
				# update value
				input_value_new = GPIO.input(11)
				if END_ROTARY == True or HOOK == True:
					break
	
			time.sleep(0.03)

			END_ROTARY = GPIO.input(12)
			HOOK = GPIO.input(13)
			while input_value_new == False:
				# update value
				input_value_new = GPIO.input(11)
				if END_ROTARY == True or HOOK == True:
					break
	
			time.sleep(0.03)

			dialed_number = dialed_number + 1
			
			END_ROTARY = GPIO.input(12)
	
		if dialed_number == 11:
			dialed_number = 0
		else:
			dialed_number = dialed_number - 1

		if dialed_number != -1:
			print dialed_number

		if dialed_number >= 0 and dialed_number <= 9:
			tel_str = tel_str + str(dialed_number) 
			number_length = number_length + 1

		dialed_number = 0

		for x in range(400):
	
			time.sleep(0.01)	
			
			END_ROTARY = GPIO.input(12)
			HOOK = GPIO.input(13)	
			
			if END_ROTARY == False:
				break	
	
			if HOOK == True:
				TIME_OUT = True
				break
		
			if number_length == 0:
				x = 0 

		if x == 399:
			print "4 seconds have passed"
			TIME_OUT = True

	# Is the phone still off hook?	
	HOOK = GPIO.input(13)
	if HOOK == False:
		# If the phone still is off hook dial now:
		print "Dial " + tel_str
		os.system("linphonecsh dial " + tel_str)

		while HOOK == False:
			HOOK = GPIO.input(13)
	
	print "User has hung up."
	os.system("linphonecsh hangup")

init_raspy()

while True:
	HOOK = GPIO.input(13)

	while (HOOK == True):
		HOOK = GPIO.input(13)
		incoming_call()
		time.sleep(0.05)

	if (HOOK == False):
		place_call()
