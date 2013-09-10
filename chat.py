#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmpp, sys, select, os
from subprocess import PIPE, Popen
from threading import Thread
try:
	from Queue import Queue, Empty
except ImportError:
	from queue import Queue, Empty
import curses
	
#get a path to ~/.xsend
path = os.path.join(os.path.expanduser('~'), '.xsend')
#try to open the file
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
q = 0

def enqueue_output(stream, q):
	for line in iter(stream, 'b'):
		q.put(line)
		print line
	stream.close()	

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
			try: line = q.get_nowait()
			except Empty:
				pass
			else:
				stdscr.addstr(line); stdscr.refresh()
		except KeyboardInterrupt:
			break

def main(stdscr):
	global handler
	global q

	curses.echo()
	curses.cbreak()
	stdscr.timeout(30)

	handler = Popen(["python", "messagehandler.py"], stdin=PIPE, stdout=PIPE, shell=True)
	q = Queue()
	t = Thread(target = enqueue_output, args = (handler.stdout, q))
	t.daemon = True
	readloop()

#set up curses
stdscr = curses.initscr()
curses.wrapper(main)
curses.endwin()
