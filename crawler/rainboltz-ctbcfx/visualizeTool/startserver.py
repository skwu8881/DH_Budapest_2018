import tornado.ioloop
import tornado.web
import eval

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("moumoukun.html")

class EvalHandler(tornado.web.RequestHandler):
    def post(self):
        article = self.get_argument("article")
        w_th = self.get_argument("w")
        c_th = self.get_argument("c")
        r_th = self.get_argument("r")
        
        res = eval.RUN_EVAL(str(article), float(w_th), float(c_th), float(r_th))
        
        self.write(res)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/eval", EvalHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()