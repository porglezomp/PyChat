#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, select, os
import subprocess
import curses
	
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

handler = 0

def readable():
	if select.select([handler.stdout,],[],[], 0.0)[0]:
		return True
	return False
	

def readloop():
	global mymessage
	curses.noecho()
	while True:
		try:
			c = stdscr.getch()
			if c != -1:
				if chr(c) == "\n" or chr(c) == "\r":
					handler.stdin.write(mymessage)
					stdscr.echochar(c)
					mymessage = ""
				elif chr(c) == "\x7F" or chr(c) == "\x08":
					stdscr.addstr("\b \b")
					mymessage = mymessage[:-1]
				else:
					stdscr.echochar(c)
					mymessage += chr(c)
			if readable():
				stdcr.addstr("Readable!")
				stdscr.addstr(handler.stdout.read())
		except KeyboardInterrupt:
			break

def main(stdscr):
	global handler
	curses.echo()
	curses.cbreak()

	handler = subprocess.Popen(["./messagehandler.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	readloop()

#set up curses
stdscr = curses.initscr()
curses.wrapper(main)
curses.endwin()
