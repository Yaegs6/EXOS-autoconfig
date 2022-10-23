import paramiko as pm
import sys
import json
import argparse 
import time 
import scrapy
from functools import reduce
import operator 

my_dict = None
switch_names = ['X440-24P-10GE4', 'X440-12P-10GE4', 'X440-48P-10GE4']                       #change these if they aren't correct but I think this is how the factory sets them up
ips = ['192.168.56.12', '192.168.56.13', '192.168.56.14']									#just add additional ip's here and change to match your network id
unknown_switches = []

class JsonRPC(object):

	def __init__(self, ipaddress, username=None, password=None, method='cli'):
		self.ipaddress = ipaddress
		self.username = username
		self.password = password
		self.transaction = 0
		self.cookie = None
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

def version_independent_input( str ):
	# This function needs to keep support for Python 2 so this function will allways use the right input method
	if sys.version_info[0] == 2 :
		return raw_input(str)
	else:
		return input(str)

def iterate_multidimensional(my_dict):
	pythondict = my_dict
	newlist = []
	ipadd = ip
	global unknown_switches

	# name = 'X440-24P-10GE4'
	#for name in switch_names:
		#iterate through python dictionary 
	for k,v in pythondict.items():   
		if(isinstance(v,dict)):
			#print(k+":")
			iterate_multidimensional(v)
			continue
		#print(k+" : "+str(v))
		#print('\n')

		#print(pythondict)
		#print('\n')
		resultdict = pythondict['result']
		#print(str(len(resultdict)) + '\n')
		#print(type(resultdict))
		#print('\n')
		#create a list from result subkey and put first entry into list 
		newdict = resultdict[0]
		for key,value in newdict.items():
			#print("Key: " + key + ", Value: " + value)
			newlist.append((str(value).split())) 		
	
	for name in switch_names:
		#check for the switch name in the newlist created from subkey 'result' as well as global switchnames list
		if name in newlist[0]:
			print(name + ' identified')
			time.sleep(5)
			#these conditional statements upload corresponding config from tftp associated with switch name
			if name == 'X440-24P-10GE4':

				jsonrpc = JsonRPC(ipaddress = ipadd, username='admin', password='', method='cli')

				cmd1 = 'upload config 192.168.56.1 newconfig.xsf vr "VR-Mgmt"'					#change ip to match your tftp server and config file name 
				cmd4 = 'load script newconfig'													#this command runs the .xsf script on the switch after its been uploaded
				#upload xsf script to switch
				response = jsonrpc.send(cmd1)

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
				#run xsf script on switch	
				response = jsonrpc.send(cmd4)

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


			elif name == 'X440-12P-10GE4':

				jsonrpc = JsonRPC(ipaddress = ipadd, username='admin', password='', method='cli')

				cmd2 = 'upload config 192.168.56.1 newconfig2.xsf vr "VR-Mgmt"'				#change ip to match your tftp server and config file name
				cmd5 = 'load script newconfig2'												#this command runs the .xsf script on the switch after its been uploaded
				#upload xsf script to switch
				response = jsonrpc.send(cmd2)

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
				#run xsf script on switch
				response = jsonrpc.send(cmd5)

				result = response.get('result')	
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

			elif name == 'X440-48P-10GE4':

				jsonrpc = JsonRPC(ipaddress = ipadd, username='admin', password='', method='cli')

				cmd3 = 'upload config 192.168.56.1 newconfig1.xsf vr "VR-Mgmt"'			#change ip to match your tftp server and config file name
				cmd6= 'load script newconfig1'											#this command runs the .xsf script on the switch after its been uploaded										   

				response = jsonrpc.send(cmd3)

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
				#send command to run xsf script and update config
				response = jsonrpc.send(cmd6)

				result = response.get('result')

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

			#shows unidentified switch name in terminal and adds that name to a list of unknown switches 
			else:
				print('Switch name: ' + name + ' not identified! Must config manually.')
				unknown_switches.append(str(name))

	return unknown_switches




def connect():
	import getpass
	global my_dict
	#establish SSH connection to switch 
	try:
		client = pm.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(pm.AutoAddPolicy())
		client.connect(ip, username='admin', password='')
		time.sleep(5)
		print('Successfully connected to ' + ip)
	except:
		print('Could not establish SSH connection to ' + ip)


	# create a JSONRPC interface object
	jsonrpc = JsonRPC(ipaddress = ip, username='admin', password='', method='cli')
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
		client.close()
	except Exception as msg:
		print (msg)
		client.close() 
	return my_dict, ip

#---------------------------------------------------------------------------------------------------------
#----------------------------------------Main Program Body------------------------------------------------
try:
	for ip in ips:
		connect()
		iterate_multidimensional(my_dict)
except KeyboardInterrupt:
	pass
#show the user the list of switches that did not get a config update
if len(unknown_switches) != 0:
	print('The following switches did not receive config: \n')
	for switch in unknown_switches:
		print(switch)
		print('\n')

print("Config update complete!")

#---------------------------------------------------------------------------------------------------------


