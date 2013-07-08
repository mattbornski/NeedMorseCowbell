#!/usr/bin/env python

import ConfigParser
import os.path
import sys

import sound

sys.path.append(os.path.join(os.path.dirname(__file__), 'thirdparty'))
import pymorse

def loadConfiguration():
	config = ConfigParser.SafeConfigParser()
	config.read(os.path.expanduser('~/.morsecowbell/config.ini'))
	return config

def service():
	config = loadConfiguration()
	encoder = pymorse.MorseCode()

	sound.play(encoder.to_morse('Hello World'))



if __name__ == '__main__':
	service()
