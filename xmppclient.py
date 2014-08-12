#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, select, os

# Try to load the user info from the .xsend file
# If the file isn't present then warn the user
path = os.path.join(os.path.expanduser('~'), '.xsend')
try:
	file = open(path, 'r')
except:
	raise IOError("No file at " + path)
FACEBOOK_ID = file.readline()
PASS = file.readline()
me = file.readline()
file.close()
current = me
mymessage = ""

# If a message has been written to stdin
def readable():
	if select.select([sys.stdin,],[],[], 0.0)[0]:
		return True
	return False
	

# This funciton selects a jid based on a normal name out of your roster of people
def selectname(name, roster):
	# Do a strict search (exact match)
	for i in roster.getItems():
   		if roster.getName(i) == name:
   			print "You are now speaking to " + roster.getName(i) + " (" + i + ")"
   			return i

	# Do a search with both pulled lowercase
	for i in roster.getItems():
		if roster.getName(i) != None:
	   		if roster.getName(i).lower() == name.lower():
	   			print "You are now speaking to " + roster.getName(i) + " (" + i + ")"
	   			return i

	# Do a search by firstname only
	for i in roster.getItems():
   		if roster.getName(i) != None:
   			firstname = roster.getName(i).split()[0]
   			if firstname.lower() == name.lower():
   				print "You are now speaking to " + roster.getName(i) + " (" + i + ")"
				return i
	# Well, we failed
	return None

def sendmsg(messagetext, to):
	global current
	if current != me:
		current = me
		print me + ": (and the above line)"
	message = xmpp.protocol.Message(to, mymessage + messagetext, typ="chat")
	jabber.send(message)

def recvmessage(conn, msg):
	global current
	global mymessage
	# Sometimes we get random empty messages, we should ignore them
	if msg.getBody() != None:
		# We only want to display messages from the person we're talking to
		if msg.getFrom() == to:
			name = rosterobject.getName(str(msg.getFrom()))
			if (name != current):
				print name + ":"
				current = name
			padding = 0
			if readable():
				newtext = sys.stdin.read()
				mymessage += newtext
				padding = len(newtext) - len(str(msg.getBody()))
				if padding < 0: padding = 0
			print "\r"+unicode(msg.getBody())+" "*padding
			sys.stdout.write(mymessage)

# This is the runloop for the client
def handle(conn):
	while True:
		try:
			conn.Process(1)
			if readable():	
				sendmsg(sys.stdin.readline(), to)
		except KeyboardInterrupt:
			break

# Get a jid and make a client
jid=xmpp.protocol.JID(FACEBOOK_ID)
sys.stdout.write("Initializing... "); sys.stdout.flush()
jabber=xmpp.Client(jid.getDomain(), debug=[])
print "done"

# Connect to the facebook server
sys.stdout.write("Connecting... "); sys.stdout.flush()
if not jabber.connect(("chat.facebook.com",5222)):
    raise IOError('Could not connect to server.')
print "done"

# Send the server the password
sys.stdout.write("Authorizing... "); sys.stdout.flush()
if not jabber.auth(jid.getNode(),PASS):
    raise IOError('Could not auth with server.')
print "done"

# Initialize presence and get the roster
sys.stdout.write("Getting roster... "); sys.stdout.flush()
jabber.sendInitPresence(requestRoster=1)
rosterobject = jabber.getRoster()
print "done"

# Set the message reception handler
jabber.RegisterHandler('message', recvmessage)
# Get the name of the target person either here or from the commandline
if len(sys.argv) < 2:
	name = raw_input("Pick someone to send to: ")
else:
	name = sys.argv[1]
to = selectname(name, rosterobject)
if (to == None):
	print "Sorry, there's nobody that fits the name '" + name + ".'"
else:
	# Initialization is done!
	print "Ready!"
	print "Type Control-C at anytime to quit."
	handle(jabber)
	print "\n\nGoodbye!\n\n"