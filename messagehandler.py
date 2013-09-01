#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, select, os, atexit, time
	
#get all the login information from .xsend
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

jabber = 0
to = 0

#this function returns true if there is anything to read on stdin
def readable():
	if select.select([sys.stdin,],[],[], 0.0)[0]:
		return True
	return False
	
#this funciton selects a jid based on a normal name
def selectname(name, roster):
	#do a strict search
	for i in roster.getItems():
   		if roster.getName(i) == name:
   			log.write("You are now speaking to " + roster.getName(i) + " (" + i + ")\n")
   			return i

	#do a lowercased search
	for i in roster.getItems():
		if roster.getName(i) != None:
	   		if roster.getName(i).lower() == name.lower():
	   			log.write("You are now speaking to " + roster.getName(i) + " (" + i + ")\n")
	   			return i

	#do a firstname search
	for i in roster.getItems():
   		if roster.getName(i) != None:
   			firstname = roster.getName(i).split()[0]
   			if firstname.lower() == name.lower():
   				log.write("You are now speaking to " + roster.getName(i) + " (" + i + ")\n")
				return i
	#well, we failed
	return None

def sendmsg(messagetext, to):
	global current
	if current != me:
		current = me
		log.write(me + ":\n")
	log.write(messagetext)
	message = xmpp.protocol.Message(to, mymessage + messagetext, typ="chat")
	jabber.send(message)

def recvmessage(conn, msg):
	global current
	if msg.getBody() != None:
		if msg.getFrom() == to:
			name = rosterobject.getName(str(msg.getFrom()))
			if (name != current):
				print name + ":"
				current = name
			padding = 0
			log.write(str(msg.getBody())+"\n")

def handle(conn):
	global mymessage
	while True:
		try:
			conn.Process(1)
			if readable():	
				sendmsg(sys.stdin.readline(), to)
		except KeyboardInterrupt:
			break

def main():
	global to
	global jabber

	#get a jid and make a client
	jid=xmpp.protocol.JID(FACEBOOK_ID)
	log.write("Initializing... ")
	jabber=xmpp.Client(jid.getDomain(), debug=[])
	log.write("done\n")
	
	#connect to the facebook server
	log.write("Connecting... ")
	if not jabber.connect(("chat.facebook.com",5222)):
	    raise IOError('Could not connect to server.')
	log.write("done\n")

	#send the server the password
	log.write("Authorizing... ")
	if not jabber.auth(jid.getNode(),PASS):
	    raise IOError('Could not auth with server.')
	log.write("done\n")

	#initialize presence and get the roster
	log.write("Getting roster... ")
	jabber.sendInitPresence(requestRoster=1)
	rosterobject = jabber.getRoster()
	log.write("done\n")

	#initialization is done!
	log.write("Ready!\n")
	log.write("Type Control-C at anytime to quit.\n")

	jabber.RegisterHandler('message', recvmessage)
	name = sys.stdin.readline().rstrip()
	to = selectname(name, rosterobject)
	handle(jabber)

log = sys.stdout#open(".runlog", 'w')
main()
log.close()
