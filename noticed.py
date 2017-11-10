#!/usr/bin/python3

VERSION = "1.1"
template = "Backend `{0}` is unreachable.%0AClient `{1}` requested page `{2}` at {3}.%0AMessage by noticed@{4}"

from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process

import urllib.parse as px

import urllib3, certifi, sys, time, configparser, os, datetime

journal = []
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
config = configparser.ConfigParser()

class errorLog():

	errdt=0.0
	fhost=''
	claddr=''
	clreq=''

	def __init__(self, dt, host, addr, req):
		self.errdt=dt
		self.fhost=host
		self.claddr=addr
		self.clreq=px.quote(req)
	def getDate(self):
		return self.errdt
	def getText(self):
		#text="Backend `{0}` is unreachable.%0AClient `{1}` requested page `{2}` at {3}.%0AMessage by noticed@{4}"
		return template.format(self.fhost, self.claddr, self.clreq, datetime.datetime.fromtimestamp(self.errdt).strftime('%H:%M:%S'), hostname)

def messaging():
	if len(journal)>0:
		msg = ''
		for i in range(0, len(journal)):
			msg+="%0A%0A"+journal[i].getText()
		http.request("GET", "https://api.telegram.org/"+botID+":"+botToken+"/sendMessage?chat_id="+chatID+"&text="+msg+"&parse_mode=markdown")
		del(journal[:])

class rqHandler(BaseHTTPRequestHandler):

	def do_HEAD(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.send_header('Access-Control-Allow-Origin', '*')
		journal.append(errorLog(time.time(), self.headers.get('host'), self.headers.get('X-Real-IP'), self.headers.get("X-Request-URI")))
		self.end_headers()

	def do_GET(self):
		self.do_HEAD()
		if ((time.time()-journal[0].getDate()>timeout) or (len(journal)>maxLogLength)):
			MessagingProcess = Process(target=messaging())
			MessagingProcess.run()
			print("")
		self.wfile.write("<!-- Noticed by Nikita Lindmann, https://ramiil.in/ https://github.com/ramiil-kun/noticed/ -->".encode("utf-8"))
		self.wfile.write(errorPage.encode("utf-8"))


print("Noticed "+VERSION+": backend failure notificator for NGINX using Telegram.")
if (len(sys.argv)>1 and sys.argv[1]=='-h'):
	print("Usage: "+sys.argv[0])
	sys.exit(0)

try:
	config.read('noticed.cfg')

	hostname = os.uname()[1]

	botID = config['Telegram']['botID']
	botToken = config['Telegram']['botToken']
	chatID = config['Telegram']['chatID']

	addr, port = config['Server']['listen'].split(":")
	errPageSource = config['Server']['errorPage']

	logFlushMode = config['Notificator']['logFlush'] #May be 'Timeout', 'Overflow', 'Both', and 'Single'
	if logFlushMode in ('Timeout', 'Both'):
		timeout = int(config['Notificator']['timeout'])
	if logFlushMode in ('Overflow', 'Both'):           
		maxLogLength = int(config['Notificator']['logLength'])

except:
	print("Error parsing config file.")

errorPage = open(errPageSource, "r").read()
print("Noticed Started")
HTTPServer((addr, int(port)), rqHandler).serve_forever()
