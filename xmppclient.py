#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, select, os, Queue, threading, ANSI, getpass, pygame
try:
        import readline
except:
        import pyreadline as readline

# Try to load the user info from the .xsend file
# If the file isn't present then warn the user
path = os.path.join(os.path.expanduser('~'), '.xsend')

passwordFound = False

try:
        file = open(path, 'r')
        # If a file is found, pull out the info and put it in some vars.
        FACEBOOK_ID = file.readline().rstrip()
        PASS = file.readline().rstrip()
        #If a password isn't found, set the bool to false
        if PASS != "":
                passwordFound = True
        me = file.readline().rstrip()
        file.close()
except:
        # If the file is not found, ask the user if they want to enter the information now.
        print "No file found at " + path
        yes = ['yes', 'y']
        no = ['no', 'n']
        choice = raw_input("Login information not found. Enter login information now?(Y/n) ").lower()
        # If the user picks yes, ask them for the information.
        if choice in yes or choice == "":
                # We use FACEBOOK_ID here because if a file is found, this section will not be called.
                FACEBOOK_ID = raw_input("Enter your Facebook ID (Example: john.smith.1@chat.facebook.com): ")
                # If you run getpass in the interactive shell, it will echo password out:
                PASS = getpass.getpass("Enter your Facebook password: ")
                passwordFound = True
                me = raw_input("Enter your Name: ")
                save = raw_input("Do you want to save your information for the next time you login?(y/N) ").lower()
                if save in yes:
                        info = open(path, 'w')
                        print "You want to save your info!"
                        savePass = raw_input ("Do you want to save your password?(Y/n) ").lower()
                        if savePass in yes or savePass == "":
                                info.write(FACEBOOK_ID+"\n"+PASS+"\n"+me)
                                print "Your information has been saved to "+path+" with your password."

                        else:
                                info.write(FACEBOOK_ID+"\n"+"\n"+me)
                                print "Your information has been saved to "+path+" WITHOUT your password."
                        info.close()

                else:
                        print "Login information not saved."

        # If the user picks NOT to enter information, close the program.
        elif choice in no:
                sys.exit(0)

        else:
                sys.exit(0)
if passwordFound != True:
        PASS = getpass.getpass("Password was not found on file. Enter your Facebook password: ")
current = me
mymessage = ""
running = True

q = Queue.Queue()

# A worker to continuously read text into the queue
def readline_worker():
        global running
        while running:
                q.put(raw_input())

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
                ANSI.ansi("A")
                print me + ":"
                ANSI.ansi("0K")
                print mymessage + messagetext
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
                        current_string = readline.get_line_buffer()
                        print "\r"+unicode(msg.getBody())+"\n"+current_string

# This is the runloop for the client
def handle(conn):
        while True:
                try:
                        conn.Process(0.2)
                        try:    
                                sendmsg(q.get_nowait(), to)
                                q.task_done()
                        except Queue.Empty:
                                pass
                except KeyboardInterrupt:
                        break

# Get a jid and make a client
jid=xmpp.protocol.JID(FACEBOOK_ID)
sys.stdout.write("Initializing... "); sys.stdout.flush()
jabber=xmpp.Client(jid.getDomain(), debug=[])
print "Done!"

# Connect to the facebook server
sys.stdout.write("Connecting... "); sys.stdout.flush()
if not jabber.connect(("chat.facebook.com",5222)):
    raise IOError('Could not connect to server.')
print "Done!"

# Send the server the password
sys.stdout.write("Authorizing... "); sys.stdout.flush()
if not jabber.auth(jid.getNode(),PASS):
    raise IOError('Could not auth with server.')
print "Done!"

# Initialize presence and get the roster
sys.stdout.write("Getting roster... "); sys.stdout.flush()
jabber.sendInitPresence(requestRoster=1)
rosterobject = jabber.getRoster()
print "Done!"

# Set the message reception handler
jabber.RegisterHandler('message', recvmessage)
# Get the name of the target person either here or from the commandline
if len(sys.argv) < 2:
        try:
                name = raw_input("Pick someone to chat with: ")
        except KeyboardInterrupt:
                print "\n\nGoodbye!\n\n"
                exit()
else:
        name = sys.argv[1]
to = selectname(name, rosterobject)
if (to == None):
        print "Sorry, there's nobody that fits the name '" + name + ".'"
else:
        # Initialization is done!
        print "Ready!"
        print "Type Control-C at anytime to quit."
        thread = threading.Thread(name="input", target=readline_worker)
        thread.start()
        handle(jabber)
        running = False
        print "\n\nGoodbye!\n\n"
