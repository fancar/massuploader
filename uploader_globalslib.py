#!/usr/bin/python3
import os
import sys
import subprocess
import socket


import csv
import json

import logging
from logging import handlers


softname = 'massuploader'
ver = 'ver. 2.810'

#HORISONTAL_LINE = 
# erase line command
if sys.platform.lower() != "win32": #POSIX
	ERASE_LINE = '\x1b[2K' 	
	SLASH = '/'
else:
	ERASE_LINE = None
	SLASH = '\\'

sep = '\n{:\u2500^70}'.format(softname+ver)

# csv default headers
hostip_header = 'ip'
login_header = 'username'
pwd_header = 'password'

#fullpath = os.path.dirname(os.path.realpath(__file__))

if getattr(sys, 'frozen', False):
        # we are running in a bundle
        #bundle_dir = sys._MEIPASS
        bundle_dir = sys.executable
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

fullpath = os.path.dirname(bundle_dir)        



logfile = fullpath+SLASH+softname+'.log'

logger = logging.getLogger(softname)
formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s\r')
stream_formatter = logging.Formatter('\n%(levelname)s: %(message)s')
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.CRITICAL)
stream_handler.setFormatter(stream_formatter)

file_handler = logging.handlers.TimedRotatingFileHandler(filename = logfile, when = 'W6', interval=1, backupCount = 8)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def ask(ask):
	ask = "press any key to "+ask+"(s/skip):"
	a = input(ask)
	if a == "s":
		print("skipped...")
		return False
	else:
		return True

def confirm(s):
	print(str(s))
	yes_tuple = ('y','yes')
	no_tuple = ('n','no')
	quit_tuple = {'q','exit','quit'}
	while True:
		try:
			q = input('(y-yes/n-no)[Q-exit]:')
			q = q.lower()
			if q in yes_tuple:
				return True
			elif q in no_tuple:
				return False
			elif q in quit_tuple:
				break
			else:
				print(' Введите "y" или "n"')
				continue
		except:
			continue
	sys.exit()		


def pingip(ip):
	'''pings ip and returns ressult'''
#win
	#CREATE_NO_WINDOW = 0x08000000
	#ping = subprocess.call("ping " + ip, creationflags=CREATE_NO_WINDOW)
#nix	
	FNULL = open(os.devnull, 'w')
	ping = subprocess.call(["ping","-c","3","-i","0.2",ip], stdout=FNULL, stderr=subprocess.STDOUT)
	if ping:
		print('No ping request from: ',ip)
		return False
	else:
		return True

def it_is_ip(ip):
	'''cheks if it is ip'''
	try:
	    socket.inet_aton(ip)
	    return True
	except socket.error:
	    return False

def csv_reader(filename,delim):
	try:
		with open(filename, "rt", encoding="windows-1251", errors='ignore') as in_csvfile:
			logger.info(f'File opened {filename}...')
			reader = csv.DictReader(in_csvfile, delimiter=delim, quotechar='|' )
			result = [row for row in reader]
			return result
	except Exception as e:
		logger.critical(f'Error opening file {filename}: {e}')
		return False