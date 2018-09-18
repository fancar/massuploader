#!/enforta/env-cfg/bin/python3.6
# 
# massuploader
#   uploads commands to a number of devices via ssh using multiprocessing.dummy
#  first try in python, no warm up at all :)
# Mamaev Alexander . fancarster@gmail.com
from multiprocessing.dummy import Pool as ThreadPool
from dicttoxml import dicttoxml
from RemoteControl_lib import *
from uploader_globalslib import *
import shutil
import sys
import socket
import paramiko
import ipaddress
import time
from datetime import datetime
from ftplib import FTP

from config import *

start_time = time.time()
sttime = datetime.now().strftime('- %Y%m%d_%H:%M:%S - ')
filenamedate = datetime.now().strftime('%d%m%Y_%H-%M.xml')


#remove empty and non ip from iplist...
#iplist = [ip for ip in iplist if ip != [] and it_is_ip(ip)]
done = failed = succeed = 0
filled_len = percents = 0



def all_items_in_dic(dic_to_check,dic_with_lists):
	'''
	 checks if all keys in dic_to_check have at least one coincide with value 
	 (with the same key) from  dic_with_lists
		 (mathces with JSON file)
	'''
	c = 0
	for key,value in dic_with_lists.items():
		for item in value:
			item_from_dic = dic_to_check[key].strip('"')
			if item[0] == '~': # the sign means slack accordance with
				item = item[1:]
				if item in item_from_dic:
					c += 1
			else:
				if item == item_from_dic: 
					c += 1
#				else:
#					logger.debug(f' the item: {item} is not in {item_from_dic}!')
	if c == len(dic_with_lists):
		#logger.debug(f' the items: "{dic_with_lists}" have been Matched!')
		return True


def read_hosts_file(filename):
	'''The func reads hosts file and returns a dictionary for the multiprocessor'''
	global main_li
	filename = fullpath+SLASH+filename
	if os.path.isfile(filename) and os.access(filename, os.R_OK):
		result = []
		if ip_only:
			logger.debug(f'ip_only mode. Opening file {filename} ...')
			result = []
			with open(filename) as f:
				li = f.read().splitlines()
				for item in li:
					if it_is_ip(item):
						result.append(item)
					else:
						logger.error(f'{item}: ip_only mode is on. The string looks not like an ip')
		else:
			whole_dic = csv_reader(filename,input_delimiter)
			if not csv_reader:
				return False
			if whole_dic:
				if extra_headers_JSON:
					try:
						with open(extra_headers_JSON, "r", encoding='utf-8') as headers_file:
							try:
								extra_headers_dic = json.load(headers_file)
								logger.debug(f'Matching values with: {extra_headers_dic} ...')
							except json.decoder.JSONDecodeError:
								logger.critical(f'Can not parse JSON file: {extra_headers_JSON}. Bad format')
								return False
						for row in whole_dic:
							if all_items_in_dic(row,extra_headers_dic):
		#							logger.debug(f'Adding a row for the ip: {row[ip_header]} ...')
								result.append(row)
					except FileNotFoundError:
						logger.critical(f' JSON file ({extra_headers_JSON}) not found')
				else:
					logger.info(f'No JSON. Using whole dic...')
					result = whole_dic
			
		if result:
			return result
		else:
			logger.critical('No matches have been found!')
			return False
	else:
		logger.critical(f'Can not open the file: {filename}')
		return False

last_line_lenght = 0

def progress(count, ip, status=''):
	global filled_len
	global percents
	global last_line_lenght
	total = hostsNo
	bar_len = 20
	local_percents = 100 * count / total
	if local_percents > percents:
		filled_len = round(bar_len * count / total)
		percents = round(local_percents)
	bar = '#' * filled_len + '=' * (bar_len - filled_len)
	LINE_TO_WRITE = '\r[%s] %s%s[%s hosts(suc:%s,fail:%s)]%s:%s' % (bar, percents, '%', total, succeed, failed, ip, status)
	if ERASE_LINE:
		sys.stdout.write(ERASE_LINE)
	else:
		if len(LINE_TO_WRITE) < last_line_lenght:
			sys.stdout.write('\r' + ' ' * last_line_lenght)

	sys.stdout.write(LINE_TO_WRITE)
	sys.stdout.flush()

	last_line_lenght = len(LINE_TO_WRITE)

def add_item_to_li(item,li):
	'''adds item on first place in list'''
	if item in li: li.remove(item)
	li.insert(0,item)
	return li
 
def add_extra_fields(input_dic):
	''' adds fields to dictionary by (reversed) list of headers if it is in main dictionary '''
	global extra_fields_li
	result = {}
	for i in extra_fields_li:
		if i in input_dic:
			result[i] = input_dic[i].strip('"')
		else:
			logger.error(f'The header {i} not found. Ignoring it...')
			extra_fields_li.remove(i)

	return result


def sendcommand(input_dic):
	''' Bruteforces logins|passwords, uploads commands from list and writes a result or an error '''
	# ip[0]
	# global logins
	# global passwords
	# global hostsNo
	global done
	global failed
	global succeed

	c = 0

	if extra_fields_li:
		result = add_extra_fields(input_dic)
	else:
		result = {}

	if ip_only:
		ip = input_dic
		lgn = pwd = None
	else:
		try:
			ip = input_dic[ip_header].strip('"')
			lgn = input_dic[username_header].strip('"')
			pwd = input_dic[password_header].strip('"')

			result[ip_header] = ip
			if not it_is_ip(ip):
				failed += 1
				done += 1
				sts = 'Error:ip not found'
				result['status'] = sts				
				progress(done, ip, status=sts)
				logger.error(f'{ip}:\t{sts}')
				return result				
		except:
			failed += 1
			done += 1
			logger.error(f'Bad input: {input_dic}')
			return


	login_list = logins
	password_list = passwords

	if lgn:
		login_list = add_item_to_li(lgn,login_list)
	if pwd:
		password_list = add_item_to_li(pwd,password_list)

	for login in login_list:
		for password in password_list:
			try:
				ssh = RemoteControl(ip,login,password)				
				sts ='Commands have been sent'
				result['status'] = sts
				for idx,cmd in enumerate(cmdlist,1):
					answer = ssh.execCommand(cmd,cmdtimeout)
					if answer:
						header = 'cmd'+str(idx)
						result[header] = '\n'.join(answer)
				done += 1
				succeed += 1
				progress(done, ip, status=sts)
				ssh.disconnect()
				logger.info(f'{ip}:\t{sts}')
				return result

			except paramiko.ssh_exception.AuthenticationException:
				progress(done, ip, status='trying another user-pass...')
			except paramiko.ssh_exception.SSHException as e:
				e = str(e)
				failed += 1
				done += 1
				sts = 'ssh error. See log'
				result['status'] = sts				
				progress(done, ip, status=sts)
				logger.error(f'{ip}:\t{sts}: {e}')
				return result

			except socket.timeout as e:
				failed += 1
				done += 1
				if 'timed out' in str(e):
					sts = 'The device is unreacheble'
				else:
					sts = 'A command was timed out'
				result['status'] = sts
				progress(done, ip, status=sts)
				logger.error(f'{ip}:\t{sts}')
				return result

			except TimeoutError:
				failed += 1
				done += 1
				sts = 'timeout!'
				result['status'] = sts
				progress(done, ip, status=sts)
				logger.error(f'{ip}:\t{sts}')
				return result

			except Exception as e:
				failed += 1
				done += 1
				e = str(e)
				unable_ssh = 'Unable to connect to port 22'
				if unable_ssh in e:
					sts = unable_ssh
				else:	
					sts = 'Unknown error: ' + e
				result['status'] = sts
				progress(done, ip, status='Error (see log)')			
				logger.error(f'{ip}:\t{sts}')
				return result


	failed += 1
	done += 1
	sts = 'Auth error'
	result['status'] = sts
	progress(done, ip, status=sts)
	logger.error(f'{ip}:\t{sts}')			
	return result		

def get_new_file(file):
	logger.info(f'Downloading file {file} drom {ftp_server}...')
	local_file = fullpath + SLASH + file
	remote_file = ftp_path + '/' + file
	tmp_data_file = fullpath + SLASH + 'tmp_data_file'
#	if os.path.isfile(tmp_data_file):

	try:
		with FTP(ftp_server, ftp_user, ftp_password, timeout=5) as ftp:
			with open(tmp_data_file, 'wb') as f:
				ftp.retrbinary('RETR ' + remote_file, f.write)
			if os.path.getsize(tmp_data_file):
				shutil.move(tmp_data_file, local_file)
				logger.info(f'File {file} has been saved!')
				return True
			else:
				logger.error(f'Downloaded file is empty!')
				return False
	except Exception as e:
		logger.critical(f' Could not download {ftp_server}. get_new_file() Error:{e}')
		return False		



def DoinParallel(li, threads=2):
    pool = ThreadPool(threads)
    results = pool.map(sendcommand, li)
    pool.close()
    pool.join()
    return results

if __name__ == "__main__":
	#check dir	

	if not os.path.exists(outputfolder):
		try:
			os.makedirs(outputfolder)
		except:
			logger.critical('can not make the folder {} for result-logs! Check the privileges!'.format(outputfolder))
			input('press Enter to exit...')
			sys.exit()

	if ftp_server:
		if get_new_file(input_file):
			print(f'{input_file} downloaded')
		else:
			if os.path.isfile(input_file):
				f_date =  time.ctime(os.path.getctime(input_file))
				logger.critical(f'Using existing file {input_file} ({f_date})')
			else:
				logger.critical(f'{input_file} the file not found')
				input('press Enter to exit...')
				sys.exit()
	
	li_of_dics = read_hosts_file(input_file)	

	if li_of_dics:
		hostsNo = len(li_of_dics)
		print('\n{:\u2500^70}'.format('The commands to be uploaded: '))
		print('\n'.join(cmdlist))
		print('\n{:\u2500^70}\n'.format(''))
		print("\n You can watch the program on AIR here:{}".format(logfile))
		print('\n{:\u2500^70}'.format('The commands to be uploaded: '))
		if confirm(f'Upload the command(s) on all {hostsNo} hosts?'):
			result = DoinParallel(li_of_dics, numthreads)

		print('\nhosts:{} | failed:{} | succeed:{}'.format(hostsNo,failed,succeed))
		print("--- %s seconds ---" % (time.time() - start_time))

		xml = dicttoxml(result, custom_root=softname, attr_type=False)
		xml = xml.decode("utf-8")
		print('Saving XML...')
		try:
			if not os.path.exists(outputfolder):
				os.makedirs(outputfolder)
			with open(outputfolder+SLASH+filenamedate, 'w', encoding='utf-8') as xml_file:
				xml_file.write(xml)
			print("\n the results have been saved in the file:{}{}{}".format(outputfolder,SLASH,filenamedate))
			print("\n See details here:{}".format(logfile))
		except:
			print('can not write to the file: {}{}{} Check the privileges!'.format(outputfolder,SLASH,filenamedate))
	#else:
	input('press any Enter to exit the program...')