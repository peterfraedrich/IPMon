#!/usr/local/python


# import stuff
import socket
import subprocess
import datetime
import smtplib
from os import stat
import time


# define vars
server_list = {}
recipiants = []
x = False


# define functions
def importHosts():

	save = open('./save', 'r')
	if stat("./save").st_size == 0:
		# get server names and load into list
		servers = open('./servers', 'r')
		for i in servers:
			a = str(i).strip('\n')
			server_list[a] = ['','','']
			print a
		saveServers()
	else:
		servers = open('./save', 'r')
		for i in servers:
			a = []
			a = str(i).strip('\n').split(',')
			server_list[a[0]] = [a[1], a[2], a[3]]

	print server_list #debug


def importRecipiants():

	emails = open('./recipiants', 'r')
	for i in emails:
		recipiants.append(str(i).strip('\n'))


def refresh():

	servers = open('./servers', 'r')
	server_list.clear()
	for i in servers:
		a = str(i).strip('\n')
		server_list[a] = ['','','']


def checkAlive():

	for i in server_list:
		print i #debug
		try:
			ping = subprocess.Popen(["ping", "-n", "3", i], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, error = ping.communicate()
			server_list[i][2] = 'up'

		except subprocess.CalledProcessError:
			server_list[i][2] = 'down'
			notify(i, server_list[i][0], server_list[i][1], 'ping')

	print server_list #debug


def dnslookup():

	for i in server_list:
		ip = socket.gethostbyname(i)
		oldip = server_list[i][1]
		server_list[i][0] = ip
		if server_list[i][0] != server_list[i][1]:
			if server_list[i][1] != '':
				notify(i, server_list[i][0], server_list[i][1], 'change')

	print server_list #debug


def notify(url, newip, oldip, event):

	if event == 'ping':
		message = "Server " + url + " at " + newip + " is not responding." + "\n" + "TIMESTAMP: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		subject = url + " is not responding."
		# do the email message thing
		sendEmail(message, subject)

	if event == 'change':
		message = "Server " + url + " has new IP at " + newip + ". Old IP was " + oldip + "\n" + "TIMESTAMP: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		subject = url + " has a new IP address."
		#do the email message thing
		sendEmail(message, subject)

		server_list[url][1] = server_list[url][0]


def sendEmail(text, subject):

	importRecipiants()

	sender = 'alerts@networkmgmt.com'
	recievers = [recipiants]

	message = """From: IP Alerts <alerts@networkmgmt.com>
	To: alerts@networkmgmt.com
	Subject: """ + subject + """

	""" + text + """ """

	try:
		smtpObj = smtplib.SMTP('localhost') 
		smtpObj.sendmail(sender, recievers, message)
		print "sent email"
		print recipiants
	except:
		print "unable to send email"


def saveServers():

	savefile = open("./save", 'w')

	for i in server_list:
		savefile.write(i + "," + server_list[i][0] + "," + server_list[i][1] + "," + server_list[i][2] + '\n')

	savefile.close()


def wait():
	time.sleep(600)


def serviceMain():

	while True:

		lastrun = int(datetime.datetime.now().strftime('%m%d')) # set date for last time this ran

		x = True # make sure loops runs

		# main loop
		while x == True:
			importHosts() # imports hosts from either servers file or save file
			checkAlive() # pings hosts to see if they're alive
			dnslookup() # looks up dns to see if server has moved
			saveServers() # save server data 
			wait() # wait 10 minutes until the next iteration
			datenowlong = int(datetime.datetime.now().strftime('%m%d%H%M')) # fix it for end of year 
			datenowshort = int(datetime.datetime.now().strftime('%m%d')) 
			if datenowlong < 12312340: # EOY fix
				if lastrun < datenowshort: # if next day, exit loop for host refresh
					print 'exiting loop'
					x = False
			else:
				print 'refreshing'
				refresh() # end of year refresh


######## MAIN SERVICE ########################
serviceMain() # do the thing