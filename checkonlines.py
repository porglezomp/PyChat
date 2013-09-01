#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, time, os

path = os.path.join(os.path.expanduser('~'), '.xsend')
try:
	file = open(path, 'r')	
except:
	raise IOError("No file " + path)
FACEBOOK_ID = file.readline()
PASS = file.readline()
file.close()
onlines = {}
changes = {}
changed = False

def presenceCB(conn, msg):
	global changed
	fr = msg.getFrom()
	if msg.getType() == None or msg.getType() == "available":
		if fr not in onlines:
			onlines[fr] = 1
			changes[fr] = "came online."
	elif msg.getType() == "unavailable":
		if fr in onlines:
			del onlines[fr]
			changes[fr] = "went offline."
	changed = True

def GoOn(conn):
	global changed
	global changes
	changes = {"You":"came online."}
	while True:
		try:
			conn.Process()
			if changed:
				changed = False
				os.system('clear')
				print "Online:"
				for person in onlines.keys():
					print rosterobject.getName(str(person))
				print
				for change in changes.keys():
					try:
						name = rosterobject.getName(str(change))
					except:
						name = change
					print name, changes[change]
				changes = {}
		except KeyboardInterrupt:
			break

#get a jid and make a client
jid=xmpp.protocol.JID(FACEBOOK_ID)
sys.stdout.write("Initializing... "); sys.stdout.flush()
jabber=xmpp.Client(jid.getDomain(), debug=[])
print "done"

#connect to the facebook server
sys.stdout.write("Connecting... "); sys.stdout.flush()
if not jabber.connect(("chat.facebook.com",5222)):
    raise IOError('Could not connect to server.')
print "done"

#send the server the password
sys.stdout.write("Authorizing... "); sys.stdout.flush()
if not jabber.auth(jid.getNode(),PASS):
    raise IOError('Could not auth with server.')
print "done"

#initialize presence and get the roster
sys.stdout.write("Getting roster... "); sys.stdout.flush()
jabber.RegisterHandler('presence', presenceCB)
jabber.sendInitPresence(requestRoster=1)
rosterobject = jabber.getRoster()
print "done"

#initialization is done!
print "Ready!"
print "Press Control-C at any time to quit."
sys.stdout.write("Starting")
for i in range(3):
	sys.stdout.flush()
	time.sleep(.15)
	sys.stdout.write(".")
	time.sleep(.15)
print
time.sleep(.5)

GoOn(jabber)

print "Goodbye!"
print
print
print
