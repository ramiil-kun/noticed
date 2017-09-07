from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import urllib3, threading, certifi, sys, getopt, time

journal = []
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())

class errorLog():

	errdt=0.0
	fhost=''
	claddr=''
	clreq=''

	def __init__(self, dt, host, addr, req):
		self.errdt=dt
		self.fhost=host
		self.claddr=addr
		self.clreq=req
	def getDate(self):
		return self.errdt
	def getText(self):
		return "Backend of `"+self.fhost+"` is unreachable.%0A"+"Client `"+self.claddr+"` requested page `"+self.clreq+"`"

class ThreadingServer(ThreadingMixIn, HTTPServer):
	pass

def msgToBot(msg):
	http.request("GET", "https://api.telegram.org/"+botID+":"+botToken+"/sendMessage?chat_id="+chatID+"&text="+msg) 

class rqHandler(BaseHTTPRequestHandler):

	def do_HEAD(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.send_header('Access-Control-Allow-Origin', '*')
		journal.append(errorLog(time.time(), self.headers.get('host'), self.headers.get('X-Real-IP'), self.headers.get("X-Request-URI")))
		self.end_headers()

	def do_GET(self):
		self.do_HEAD()
		if ((time.time()-journal[0].getDate()>10) or (len(journal)>10)):
			msg = ''
			for i in range(1, len(journal)):
				msg+="%0A%0A"+journal[i].getText()
			msgToBot(msg)
			del(journal[:])
		self.wfile.write(errorPage.encode("utf-8"))

print("Noticed is backend failure notificator for NGINX using Telegram.")
if (len(sys.argv)!=5):
	print("Usage: "+sys.argv[0]+" <Bot ID> <Bot Token> <Telegram Chat ID> <Error Page>")
	print("Copy noticed.conf into your nginx directory and add 'include noticed.conf' into your server{} block.")

	sys.exit(0)
else:
	botID = sys.argv[1]
	botToken = sys.argv[2]
	chatID = sys.argv[3]
	errPageSource = sys.argv[4]

errorPage = open(errPageSource, "r").read()
print("Noticed Started")
ThreadingServer(('127.0.0.1', 8081), rqHandler).serve_forever()
