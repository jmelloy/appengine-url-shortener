import os
import logging

import webapp2
import jinja2

from models import *
import base62
import datetime

template_path = os.path.join(os.path.dirname(__file__), "templates")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class BasePage(webapp2.RequestHandler):
    def render(self, template, values=None):
        if not values:
            values = {}
        template = JINJA_ENVIRONMENT.get_template(template)
        self.response.out.write(template.render(values))


class Index(BasePage):
    """
    Homepage where User submits URL to be shortened.
    """

    def get(self):
        self.render("index.html", {})

    def post(self):
        url = self.request.get("url")
        custom_path = self.request.get("custom_path")
        if custom_path:
            exists = Link.get_by_id(custom_path)
            if exists:
                return "path already exists, choose another"
        else:
            id = Counter.increment()
            custom_path = base62.base62_encode(id)

        l = Link(url=url, custom_path=custom_path, id = custom_path)
        l.put()

        self.redirect("/" + custom_path + "/stats")

class Stats(BasePage):
    """
    Show stats for most recent and most followed links.
    """

    def get(self, code):

        l = Link.get_by_id(code)

        self.render("stats.html", {"l": l})

class Expand(BasePage):
    """
    Get the target URL given the shortened path.
    """

    def get(self, path):
        linkobj = Link.get_by_id(path)
        #account for 404, log it.
        linkobj.count += 1
        linkobj.put()

        le = LinkExpand(code = path,
                        timestamp=datetime.datetime.now(),
                        ip_address=self.request.remote_addr,
                        header = [Header(Key=k, Value=v) for k,v in self.request.headers.items()]
                        )
        le.put()

        self.redirect(str(linkobj.url))

app = webapp2.WSGIApplication([
    ("/", Index),
    ("/(.+)/stats", Stats),
    ("/(.+)", Expand),
    ], debug=True)
