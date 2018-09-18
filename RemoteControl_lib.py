#!/usr/local/bin/python
# coding=utf-8
# ver 0.9 added wlan ip lookup

from paramiko import SSHClient
from paramiko import AutoAddPolicy
from uploader_globalslib import *
from config import *

class RemoteControl:
	ssh = None

	def __init__(self, host, login, password):
		ssh = SSHClient()
		ssh.set_missing_host_key_policy(AutoAddPolicy())
		#, auth_timeout=auth_timeout, banner_timeout=banner_timeout
		logger.debug(f'{host}:\t connecting...')
		ssh.connect(host, port=22, username=login, password=password, timeout=timeout,allow_agent=False,look_for_keys=False,auth_timeout=au_timeout,banner_timeout=bn_timeout) #auth_timeout=au_timeout,banner_timeout=bn_timeout
		logger.debug(f'{host}:\tConnected! {login}\\{password} fits!')
		self.host = host
		self.ssh = ssh

	def execCommand(self,cmd,timeout):
		stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout, get_pty=False)  # 
		result = []
		for i in stdout.readlines():
			result.append(i.strip())
		answer = '\n'.join(result)
		logger.debug(f'{self.host}:\tSent: {cmd}')
		if len(answer) > 0:
			logger.debug(f'{self.host}:\tIt answered: {answer}')			
		return result

	def disconnect(self):
		if self.ssh:
			self.ssh.close()
			logger.debug(f'{self.host}:\tDisconnected!')
			self.ssh = None

	def __del__(self):
		if self.ssh:
			self.ssh.close()
			self.ssh = None






