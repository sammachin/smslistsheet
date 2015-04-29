import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
from twilio import twiml
import gspread

user = 'sam.machin@gmail.com'
pw = "mechjkhfxdvbszng"

def isadmin(number):
	gc = gspread.login(user, pw)
	worksheet = gc.open("smslist").worksheet("admins")
	try:
		sender = worksheet.find(number)
	except:
		sender = None
	if sender == None:
		return False
	else:
		return True



class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.content_type = 'text/plain'
		self.write("SMS List Sheet")
		self.finish()

		
class MsgHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		text = self.get_argument("Body")
		sender = self.get_argument("From")
		if isadmin(sender):
			gc = gspread.login(user, pw)
			membersheet = gc.open("smslist").worksheet("members")
			members = membersheet.row_values(1)
			r = twiml.Response()
			for member in members:
				if member != None:
					r.message("Test", From="441172001500", To=member)
		else:
			r = twiml.Response()
			r.message("Sorry message not recognised")
		self.content_type = 'text/xml'
		self.write(str(r))
		self.finish()


def main():
	static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	print static_path
	application = tornado.web.Application([(r"/", MainHandler),
											(r"/message", MsgHandler),
											(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
											])
	http_server = tornado.httpserver.HTTPServer(application)
	port = int(os.environ.get("PORT", 5000))
	http_server.listen(port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
	
	

