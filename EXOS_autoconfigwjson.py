#!/usr/bin/env python

# --------------------------------------------------------------------------- #
# Script that iterates through json file containing switch names, ip's, and   #
# tftpd64 .xsf config filenames and downloads .xsf from server to switch.     #
# The json file can be added to or changed as needed and the script will      #
# still function the same.                                                    #
# --------------------------------------------------------------------------- #

import paramiko as pm
import sys
import json
import argparse 
import time 
import scrapy
from functools import reduce
import operator 


client = None

class JsonRPC(object):

	def __init__(self, ipaddress, username=None, password=None, method='cli'):
		self.ipaddress = ipaddress
		self.username = username
		self.password = password
		self.transaction = 0
		self.cookie = None
		self.client = None
		# construct a URL template for the EXOS JSONRPC POST message
		self.url = 'http://{ip}/jsonrpc'.format(ip=self.ipaddress)
		self.json_request = {'method' : method,
							'id' : self.transaction,
							'jsonrpc' : '2.0',
							'params' : None
							}
	def send(self, cmds):
		# This method:
		#   fills out the JSONRPC POST data structures
		#   Sends the POST via HTTP to the EXOS switch
		#   gets the POST response
		#   returns the decoded JSON in native python structures

		import requests

		# http headers
		headers = {'Content-Type': 'application/json'}

		# after the first authentication, EXOS returns a cookie we can use
		# in JSONRCP transactions to avoid re-authenticating for every transaction
		#
		# if we have a cookie from previsous authentication, use it
		if self.cookie is not None:
			headers['Cookie'] = 'session={0}'.format(self.cookie)

		# increment the JSONRPC transaction counter
		self.transaction += 1
		self.json_request['id'] = self.transaction

		# JSONRPC defines params as a list
		# EXOS expects the CLI command to be a string in a single list entry
		self.json_request['params'] = [cmds]

		# send the JSONRPC message to the EXOS switch
		response = requests.post(self.url,
			headers=headers,
			auth=(self.username, self.password),
			data=json.dumps(self.json_request))

		# interpret the response from the EXOS switch
		# first check the HTTP error code to see if HTTP was successful
		# delivering the message
		if response.status_code == requests.codes.ok:
			# if we have a cookie, store it so we can use it later
			self.cookie = response.cookies.get('session')
			try:
				# ensure the response is JSON encoded
				jsonrpc_response = json.loads(response.text)

				# return the JSONRPC response to the caller
				return jsonrpc_response
			except:
				return None

			# raise http exception

		response.raise_for_status()


def connect(ip):
	global client
	import getpass
	#establish SSH connection to switch 
	try:
		client = pm.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(pm.AutoAddPolicy())
		client.connect(ip, username='admin', password='')
		time.sleep(8)
		print('Successfully connected to ' + ip)
	except:
		print('Could not establish SSH connection to ' + ip)
		return client

def connectionmessage(ip, jsonrpc):
	cmd = 'show switch'

	try:
		# send the command to the EXOS switch over HTTP. the object will do the proper encoding
		response = jsonrpc.send(cmd)
		#dump the json response to a string 
		jsonstr = (json.dumps(response, indent=2, sort_keys=True))
		#load the json response to dictionary
		my_dict = json.loads(jsonstr)
		# dump the JSONRPC response to the user in a pretty format
		# first the data stuctures
		result = response.get('result')
		#display the cli output to remote terminal to monitor progress
		try:
			if result is not None:
				cli_output = result[0].get('CLIoutput')
				if cli_output is not None:
					print ('\nFormatted CLIoutput Display')
					print ('*' * 80)
					print (cli_output)
					print ('*' * 80)
		except:
			pass
		#client.close()
	except Exception as msg:
		print (msg)
		#client.close() 
	return ip

def sendcmd(cmd, jsonrpc):
	#upload xsf script to switch
	response = jsonrpc.send(cmd)

	result = response.get('result')
	#prints the clioutput to the terminal
	try:
		if result is not None:
			cli_output = result[0].get('CLIoutput')
			if cli_output is not None:
				print ('\nFormatted CLIoutput Display')
				print ('*' * 80)
				print (cli_output)
				print ('*' * 80)
	except:
		pass	

def main():
	global client
	# open the json file
	with open('filepath to your json file') as json_file: # put your json filepath here
		data = json.load(json_file)

		# loop through switches in json file 
		for i in data['Switches']:
			ip = i['ip']
			name = i['name']
			config = i['config']

			# SSH connection to switch
			connect(ip)
			time.sleep(3)

			jsonrpc = JsonRPC(ipaddress = ip, username='admin', password='', method='cli')

			connectionmessage(ip, jsonrpc)

			# this command gets the .xsf script from the tftpd server and loads it on the switch
			getconfig = 'tftp get "your tftp server ip here" vr VR-Mgmt ' + config 	# where you put your tftp server ip
			# this command runs the .xsf script on the switch after its been uploaded								
			loadscript = 'load script ' + config													

			# send command to get .xsf from tftpd
			sendcmd(getconfig, jsonrpc)
			time.sleep(1)

			# send command to run script on switch
			sendcmd(loadscript, jsonrpc)
			time.sleep(1)

			client.close()
				
if __name__ == '__main__':
	main()