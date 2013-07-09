import email
import getpass
import imaplib
import json
import os
import os.path
import sys
import time
import traceback

PREFIX = os.path.splitext(os.path.basename(__file__))[0].upper() + '_'
def parseConfiguration(env):
	return {k.split(PREFIX)[1]: json.loads(v) for (k, v) in env.iteritems() if k.startswith(PREFIX)}

def configure(env):
	config = parseConfiguration(env)
	ret = {}

	defaultHost = config.get('HOST', 'imap.gmail.com')
	host = raw_input('IMAP host? [{defaultHost}] '.format(defaultHost=defaultHost))
	if host == '':
		host = defaultHost
	print host
	ret['HOST'] = host

	defaultSSL = config.get('SSL', True)
	ssl = raw_input('IMAP using SSL/TLS (true/false)? [{defaultSSL}] '.format(defaultSSL=defaultSSL)).lower()
	if ssl == '':
		ssl = defaultSSL
	print ssl
	truth = {
		True: True,
		False: False,
		't': True,
		'f': False,
		json.dumps(True): True,
		json.dumps(False): False,
	}
	ret['SSL'] = truth[ssl]

	defaultPort = config.get('PORT', (993 if ret['SSL'] else 143))
	port = raw_input('IMAP port? [{defaultPort}] '.format(defaultPort=defaultPort))
	if port == '':
		port = defaultPort
	print port
	ret['PORT'] = int(port)

	defaultUsername = config.get('USERNAME', getpass.getuser())
	username = raw_input('IMAP username? [{defaultUsername}] '.format(defaultUsername=defaultUsername))
	if username == '':
		username = defaultUsername
	print username
	ret['USERNAME'] = username

	existingPassword = config.get('PASSWORD')
	defaultPasswordPlaceholderIfAppropriate = ''
	if existingPassword is not None:
		defaultPasswordPlaceholderIfAppropriate = '[' + '*' * len(defaultPassword) + '] '
	password = ''
	while password == '':
		password = raw_input('IMAP password? {defaultPasswordPlaceholderIfAppropriate}'.format(defaultPasswordPlaceholderIfAppropriate=defaultPasswordPlaceholderIfAppropriate))
	print password
	ret['PASSWORD'] = password

	return {PREFIX + k: json.dumps(v) for (k, v) in ret.iteritems()}

def connection(config):
	cls = (imaplib.IMAP4_SSL if config['SSL'] == True else imaplib.IMAP4)
	mailbox = cls(config['HOST'], config['PORT'])
	mailbox.login(config['USERNAME'], config['PASSWORD'])
	mailbox.select(readonly=True)
	return mailbox

def configured(env):
	config = parseConfiguration(env)

	try:
		mailbox = connection(config)
		mailbox.close()
		mailbox.logout()
		return True
	except:
		for line in traceback.format_exc().splitlines():
			print >> sys.stderr, line
		return False

def serve():
	config = parseConfiguration(os.environ)
	mailbox = connection(config)
	(result, data) = mailbox.uid('search', None, 'ALL')
	latestUid = int(data[0].split()[-1])

	while True:
		(result, data) = mailbox.uid('search', None, '(UID {latestUid}:*)'.format(latestUid=str(latestUid)))
		uids = [int(uid) for uid in data[0].split() if int(uid) > latestUid]
		
		for uid in uids:
			(result, data) = mailbox.uid('fetch', str(uid), '(RFC822)')
			message = email.message_from_string(data[0][1])
			print message['subject']
			sys.stdout.flush()

		latestUid = max(uids + [latestUid])
		time.sleep(10)
		# Refresh
		mailbox.recent()

if __name__ == '__main__':
	serve()
