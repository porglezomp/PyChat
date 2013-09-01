#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, select, os
	
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

def readable():
	if select.select([sys.stdin,],[],[], 0.0)[0]:
		return True
	return False
	

#this funciton selects a jid based on a normal name
def selectname(name, roster):
	#do a strict search
	for i in roster.getItems():
   		if roster.getName(i) == name:
   			print "You are now speaking to " + roster.getName(i) + " (" + i + ")"
   			return i

	#do a lowercased search
	for i in roster.getItems():
		if roster.getName(i) != None:
	   		if roster.getName(i).lower() == name.lower():
	   			print "You are now speaking to " + roster.getName(i) + " (" + i + ")"
	   			return i

	#do a firstname search
	for i in roster.getItems():
   		if roster.getName(i) != None:
   			firstname = roster.getName(i).split()[0]
   			if firstname.lower() == name.lower():
   				print "You are now speaking to " + roster.getName(i) + " (" + i + ")"
				return i
	#well, we failed
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
	if msg.getBody() != None:
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
			print "\r"+str(msg.getBody())+" "*padding
			sys.stdout.write(mymessage)

def handle(conn):
	while True:
		try:
			conn.Process(1)
			if readable():	
				sendmsg(sys.stdin.readline(), to)
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
jabber.sendInitPresence(requestRoster=1)
rosterobject = jabber.getRoster()
print "done"

#initialization is done!
print "Ready!"
print "Type Control-C at anytime to quit."

jabber.RegisterHandler('message', recvmessage)
if len(sys.argv) < 2:
	name = raw_input("Pick someone to send to: ")
else:
	name = sys.argv[1]
to = selectname(name, rosterobject)
handle(jabber)
print "\n\nGoodbye!\n\n"
