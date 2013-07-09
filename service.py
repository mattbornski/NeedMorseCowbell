#!/usr/bin/env python

import ConfigParser
import json
import os.path
import Queue
import subprocess
import sys
import threading
import time
try:
	import unidecode
except ImportError:
	class FakeUnidecode(object):
		def unidecode(text):
			return text
	unidecode = FakeUnidecode()

import plugins
import sound

sys.path.append(os.path.join(os.path.dirname(__file__), 'thirdparty'))
import pymorse

CONFIG_PATH = os.path.expanduser('~/.morsecowbell/config.ini')

# With thanks to http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
def enqueueOutput(outputStream, outputQueue):
	for line in iter(outputStream.readline, b''):
		print line
		outputQueue.put(line)
	outputStream.close()

def runPlugin(plugin, env, stdoutQueue, stderrQueue):
	p = subprocess.Popen('python ' + plugin.__file__, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, close_fds=('posix' in sys.builtin_module_names), env=env, shell=True)
	stdoutThread = threading.Thread(target=enqueueOutput, args=(p.stdout, stdoutQueue))
	stdoutThread.daemon = True
	stdoutThread.start()
	stderrThread = threading.Thread(target=enqueueOutput, args=(p.stderr, stderrQueue))
	stderrThread.daemon = True
	stderrThread.start()

def loadConfiguration():
	config = ConfigParser.SafeConfigParser()
	config.read(CONFIG_PATH)
	return config

def saveConfiguration(config):
	if not os.path.exists(os.path.dirname(CONFIG_PATH)):
		os.mkdir(os.path.dirname(CONFIG_PATH))
	with open(CONFIG_PATH, 'wb') as f:
		config.write(f)

def service():
	config = loadConfiguration()
	# If this appears to be a first-run, initialize a config file
	if not config.has_section('general'):
		config.add_section('general')
		config.set('general', 'quiet', json.dumps(False))
		saveConfiguration(config)

	# Do not error out on unencodable characters
	encoder = pymorse.MorseCode(strict_mode=False)
	# In case of unencodable characters:
	# Try lossy conversion of unicode or accented characters to their nearest basic Latin character
	def downconverter(text):
		if isinstance(text, unicode):
			return pymorse.MorseCode.to_morse(encoder, unidecode.unidecode(text))
		else:
			return pymorse.MorseCode.to_morse(encoder, text)
	encoder.to_morse = downconverter
	# If that doesn't work, use a ?
	encoder.missing_morse_code_placeholder = '?'

	if not json.loads(config.get('general', 'quiet')):
		sound.play(encoder.to_morse('Hello World'))

	stdoutQueue = Queue.Queue()
	stderrQueue = Queue.Queue()

	for pluginName in plugins.__dict__:
		if not pluginName.startswith('_'):
			plugin = plugins.__dict__.get(pluginName)

			prefix = pluginName.upper() + '_'
			env = os.environ.copy()
			try:
				for (k, v) in config.items(pluginName):
					env[k.upper()] = v
			except ConfigParser.NoSectionError:
				pass

			if not plugin.configured(env):
				print pluginName + ' requires configuration'
				settings = plugin.configure(env)
				config.remove_section(pluginName)
				config.add_section(pluginName)
				env = os.environ.copy()
				for (k, v) in settings.iteritems():
					config.set(pluginName, k.upper(), v)
					env[k.upper()] = v
				# Write out the config changes
				saveConfiguration(config)
			
			runPlugin(plugin, env, stdoutQueue, stderrQueue)

	while True:
		try:
			print >> sys.stderr, stderrQueue.get_nowait().strip()
		except Queue.Empty:
			pass
		try:
			text = stdoutQueue.get_nowait().strip()
			print text
			sound.play(encoder.to_morse(text))
		except Queue.Empty:
			pass

# Install and configure to start at boot/login
def install():
	pass



if __name__ == '__main__':
	service()
