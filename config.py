#!/usr/bin/python3
# -*- coding: utf-8 -*-
#config file of the program
import configparser
from uploader_globalslib import *
#config
print(sep)


configfile = 'config.ini'

ip_header = 'ip_address'
username_header = 'username'
password_header = 'password'


yes_tuple = ('y','yes')
no_tuple = ('n','no')
none_tuple = ('none')
quit_tuple = ('q','exit','quit')
	
cfg = configparser.ConfigParser()
cfg.read(configfile)

try:
	cfg_main = cfg['main']
	cfg_timeouts = cfg['timeouts']
	cfg_upload = cfg['upload']
	cfg_commands = cfg['commands']
	output_xml = cfg['output_xml']
except:
	logger.critical(f'some of sections (main,timeouts,upload,commands,output_xml) have not been found')
	logger.critical(f'bad config file! Check: {configfile}')
	input("press any key to exit the programm...")
	sys.exit()

##[main] section
try:
	numthreads = int(cfg_main['numthreads'])
	logger.info(f'Number of threads: {numthreads}')
except:
	numthreads = 10
	logger.critical(f'using default number of threads: {numthreads}')

ip_only = ftp_server = False
extra_headers_JSON = None
extra_fields_li = None
try:
	input_type = cfg_main['input_type']
	if input_type == 'txt':
		ip_only = True
		logger.info('Input format data: txt (ip addresses line by line)')
	elif input_type == 'csv':		
		try:
			input_delimiter = cfg_main['input_delimiter']
		except:
			logger.critical('error getting "input_delimiter" value from [main] section of config-file!')
			input("press any key to exit the programm...")
			sys.exit()

		try:
			ip_header = cfg_main['ip_header']
			username_header = cfg_main['username_header']
			password_header = cfg_main['password_header']
			logger.info(f'The header for ip: {ip_header} ; The header for username: {username_header} ; The header for password: {password_header}')
		except:
			logger.critical('error getting "ip_header" values from [main] section of config-file!')
			input("press any key to exit the programm...")
			sys.exit()

		try:
			extra_headers_JSON = cfg_main['extra_headers_JSON']
			if extra_headers_JSON.lower() in none_tuple:
				extra_headers_JSON = None
				logger.info('No JSON chosen')
			else:		
				logger.info(f'json: {extra_headers_JSON}')
		except:
			logger.critical('error getting "extra_headers_JSON" value from [main] section of config-file!')
			input("press any key to exit the programm...")
			sys.exit()

		try:
			extra_fields_str = output_xml['extra_fields_order']
			if not extra_fields_str.lower() == 'none':
				extra_fields_li = [x.strip('"') for x in extra_fields_str.split(',')]
				extra_fields_li.reverse()
			else:
				extra_fields_li = None

		except:
			outputfolder = 'results'
			logger.critical(f'Parameter "extra_fields_order" have not been found in ini file')
			if confirm('Countinue without extra_fields in output file?'):
				extra_fields_li = None
			else:
				sys.exit()

		logger.info('Input format data: CSV')


	else:
		logger.critical('error getting "input_type" value from [main] section of config-file! set "yes" or "no"input_delimiter')
		input("press any key to exit the programm...")
		sys.exit()
except:
	logger.critical('error getting "input_type" value from [main] section of config-file!')
	input("press any key to exit the programm...")
	sys.exit()

try:
	ftp_server = cfg_main['ftp_server']
	if ftp_server.lower() == 'none':
		ftp_server = None
	else:
		ftp_user = cfg_main['ftp_user']
		if ftp_user.lower() == 'none': ftp_user = None

		ftp_password = cfg_main['ftp_password']
		if ftp_password.lower() == 'none': ftp_password = None
		
		ftp_path = cfg_main['ftp_path']
		logger.info(f'FTP server: {ftp_server} ; remote_path:{ftp_path}')
except:	
	logger.critical('error getting FTP values from [main] section of config-file!')
	input("press any key to exit the programm...")
	sys.exit()	
# except:
# 	logger.warning('error getting ftp_server value from [main] section of config-file! Ignoring  ftp...')

try:
	loginstr = cfg_main['logins']
	logins = loginstr.split(',')
	pwdstr = cfg_main['passwords']
	passwords = pwdstr.split(',')
except:
	logger.critical('error getting usernames and/or passwords in config file. Set at least one pair!')
	input("press any key to exit the programm...")
	sys.exit()

try: 
	input_file = cfg_main['input_file']
	logger.info(f'input file: {input_file}')
except:
	logger.critical("Set hosts value (name of a csv with ip;user;password) in config.ini file first! ")
	input("press any key to exit the programm...")
	sys.exit()

## [timeouts] section	

try: 
	timeout = int(cfg_timeouts['timeout'])
	logger.info(f'timeout: {timeout}')
except:
	timeout = 3
	logger.critical(f'using default ssh timeout: {timeout}')

try: 
	bn_timeout = cfg_timeouts['banner_timeout']
	logger.info(f'Banner timeout: {bn_timeout}')
	if bn_timeout.lower() == 'none':
		bn_timeout = None
	else:
		bn_timeout = int(bn_timeout)
except:
	bn_timeout = None
	logger.critical(f'using default ssh banner-timeout: {bn_timeout}')

try:
	au_timeout = cfg_timeouts['auth_timeout']
	logger.info(f'Auth timeout: {au_timeout}')
	if au_timeout:
		au_timeout = int(au_timeout)
except:
	au_timeout = None
	logger.critical(f'using default ssh auth_timeout: {au_timeout}')


try:
	cmdtimeout = cfg_timeouts['cmdtimeout']
	logger.info(f'CMD timeout: {au_timeout}')
	if cmdtimeout == 'None':
		cmdtimeout = None
	elif cmdtimeout.isdigit():
		cmdtimeout = int(cmdtimeout)
	else:
		cmdtimeout = 5
		logger.critical(f'Bad cmdtimout value. Using default command exec-timeout: {cmdtimeout}')	
except:
	cmdtimeout = 5
	logger.critical(f'using default command exec-timeout: {cmdtimeout}')



#[commands] section

try:
	commands = cfg_commands['commands']
	with open(commands) as f:
		cmdlist = f.read().splitlines()	
except:
	print(" Set file name with commands in config.ini file first! (Variable commands) ")
	input("press any key to exit the programm...")
	sys.exit()		

try:
	outputfolder = output_xml['outputfolder']
except:
	outputfolder = 'results'
	logger.critical(f'Outputfolder value not found. Using default folder-name: {outputfolder}')


