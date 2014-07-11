#!/usr/bin/python


# import stuff
import socket
import subprocess
import datetime
import smtplib
from os import stat
import time
import sys


# define vars
server_list = {}
recipiants = []
x = False

def savefile():
	save = open('./save', 'w')
	save.close()

savefile()

# define functions
def lognew():
	filename = './logfile' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	log = open('./logfile', 'r')
	oldlog = open(filename, 'w')
	for i in log:
		oldlog.write(i)

	oldlog.close()
	log.close()
	log = open('./logfile', 'w')
	log.close()


def logadd(msg):

	ts = str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
	log = open('./logfile', 'a')
	log.write(ts + " : " + str(msg) + '\n')
	log.close()


def importHosts():

	save = open('./save', 'r')
	if stat("./save").st_size == 0:
		# get server names and load into list
		servers = open('./servers', 'r')
		for i in servers:
			a = str(i).strip('\n')
			server_list[a] = ['','','']
		saveServers()
		logadd('INFO -- got new hosts from servers file')
	else:
		servers = open('./save', 'r')
		for i in servers:
			a = []
			a = str(i).strip('\n').split(',')
			server_list[a[0]] = [a[1], a[2], a[3]]
		logadd('INFO -- imported save file into server_list dict')


def importRecipiants():

	emails = open('./recipiants', 'r')
	for i in emails:
		recipiants.append(str(i).strip('\n'))
	logadd('INFO -- imported recipiant email addresses into recipiants list obj')


def refresh():

	servers = open('./servers', 'r')
	server_list.clear()
	for i in servers:
		a = str(i).strip('\n')
		server_list[a] = ['','','']
	logadd('INFO -- refreshed the server_list dict')


def checkAlive():

	logadd('INFO -- began checking servers')
	for i in server_list:
		response = os.system("ping -W 100 -c 3 " + server_list[i][1] + " > /dev/null 2>&1")
        if response == 0:
    	    server_list[i][2] = 'up'
			msg = 'PING CHECK -- domain ' + i + ' is UP.'
			logadd(msg)
			print msg        
        else:
        	server_list[i][2] = 'down'
			notify(i, server_list[i][0], server_list[i][1], 'ping')
			msg = 'PING CHECK -- domain ' + i + ' is DOWN.'
			logadd(msg)
			print msg
            

	#	try:
	#		ping = subprocess.Popen(["ping", "-n", "3", server_list[i][1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#		out, error = ping.communicate()
	#		server_list[i][2] = 'up'
	#		msg = 'PING CHECK -- domain ' + i + ' is UP.'
	#		logadd(msg)
	#		print msg
	#
	#	except: #subprocess.CalledProcessError:
	#		server_list[i][2] = 'down'
	#		notify(i, server_list[i][0], server_list[i][1], 'ping')
	#		msg = 'PING CHECK -- domain ' + i + ' is DOWN.'
	#		logadd(msg)
	#		print msg


def dnslookup():

	logadd('INFO -- begin DNS lookups')
	for i in server_list:
		try:
			wait(3) # wait to make sure DNS servers don't get pissy
			ip = socket.gethostbyname(i)
			oldip = server_list[i][1]
			server_list[i][0] = ip
			msg = 'DNS RESOLVE -- ' + i + ' resolves to ' + ip 
			logadd(msg)
			print msg
			if server_list[i][0] != server_list[i][1]:
				if server_list[i][1] != '':
					notify(i, server_list[i][0], server_list[i][1], 'change')
					msg = ' DNS WARN -- domain ' + i + 'changed IP address to ' + server_list[i][0]
					logadd(msg)
					print msg
							
		except socket.gaierror:
			notify(i, 'null', 'null', 'resolve')
			


def notify(url, newip, oldip, event):

	if event == 'ping':
		message = "Server " + url + " at " + newip + " is not responding." + "\n" + "TIMESTAMP: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		subject = url + " is not responding."
		# do the email message thing
		sendEmail(message, subject)
		msg = 'NOTIFY -- ' + "Server " + url + " at " + newip + " is not responding."
		logadd(msg)
		print msg

	if event == 'change':
		message = "Server " + url + " has new IP at " + newip + ". Old IP was " + oldip + "\n" + "TIMESTAMP: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		subject = url + " has a new IP address."
		#do the email message thing
		sendEmail(message, subject)
		msg = 'NOTIFY -- ' + "Server " + url + " has new IP at " + newip + ". Old IP was " + oldip
		logadd(msg)
		server_list[url][1] = server_list[url][0]
		print msg

	if event == 'resolve':
		message = "Server " + url + " could not be resolved" + "\n" + "TIMESTAMP: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		subject = url + " could not be resolved."
		#do the email message thing
		sendEmail(message, subject)
		msg = 'DNS WARN -- domain ' + url + ' could not be resolved'
		logadd(msg)
		print msg


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
		logadd('INFO -- Notification email sent')
	except:
		logadd('ERROR -- unable to send mail')
		print 'ERROR -- unable to send mail'


def saveServers():

	savefile = open("./save", 'w')

	for i in server_list:
		savefile.write(i + "," + server_list[i][0] + "," + server_list[i][1] + "," + server_list[i][2] + '\n')

	savefile.close()
	logadd('INFO -- servers save to save file')


def wait(sec):
	time.sleep(int(sec))


def serviceMain():

	logadd('STARTUP -- the app started up OK')
	print 'IPMon is now running.'
	
	# check for cli args
	if len(sys.argv) < 1:
		if sys.argv[1] == '-r':
			refresh()
			logadd('INFO -- user refresh')

	while True:

		lastrun = int(datetime.datetime.now().strftime('%m%d')) # set date for last time this ran
		lognew()
		refresh()

		x = True # make sure loops runs

		# main loop
		while x == True:
			importHosts() # imports hosts from either servers file or save file
			dnslookup() # looks up dns to see if server has moved
			checkAlive() # pings hosts to see if they're alive
			saveServers() # save server data 
			wait(300) # wait 10 minutes until the next iteration
			datenowlong = int(datetime.datetime.now().strftime('%m%d%H%M')) # fix it for end of year 
			datenowshort = int(datetime.datetime.now().strftime('%m%d')) 
			if datenowlong < 12312340: # EOY fix
				if lastrun < datenowshort: # if next day, exit loop for host refresh
					logadd('INFO -- exited loop to refresh')
					x = False
			else:
				refresh() # end of year refresh
				logadd('INFO -- exited loop for EOY refresh')


######## MAIN SERVICE ########################
serviceMain() # do the thing

# EOF