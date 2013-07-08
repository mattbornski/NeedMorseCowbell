import os
import os.path
import sys
import tempfile
import wave

DIT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'wav', 'dit.wav'))
DAH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'wav', 'dah.wav'))
GAP = os.path.abspath(os.path.join(os.path.dirname(__file__), 'wav', 'gap.wav'))

try:
	import winsound
	_play = lambda filename: winsound.PlaySound(filename, None)
except ImportError:
	import subprocess
	command = {
		'darwin': 'afplay',
	}.get(sys.platform, 'mpg123')
	_play = lambda filename: subprocess.check_call('{command} {filename}'.format(command=command, filename=filename), shell=True)

def bufferFilename(filename):
	waveRead = wave.open(filename, 'rb')
	try:
		return (waveRead.getparams(), waveRead.readframes(waveRead.getnframes()))
	finally:
		waveRead.close()

def play(morseCode):
	# Concatenate the files together
	buffers = {}
	params = None
	frames = None
	for character in morseCode:
		filename = {
			'.': DIT,
			'-': DAH,
			' ': GAP,
		}.get(character)
		if filename is not None:
			if filename not in buffers:
				(p, f) = bufferFilename(filename)
				buffers[filename] = f
				if params is None:
					params = p
			if frames is None:
				frames = buffers[filename]
			else:
				frames += buffers[filename]

	# Write to temp file
	filename = tempfile.NamedTemporaryFile().name
	waveWrite = wave.open(filename, 'wb')
	try:
		waveWrite.setparams(params)
		waveWrite.writeframes(frames)
	finally:
		waveWrite.close()

	# Play sound
	try:
		_play(filename)
	finally:
		os.remove(filename)

if __name__ == '__main__':
	play('... --- ...')
