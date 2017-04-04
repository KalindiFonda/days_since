# Code to render content to be hosted on google app engine
import os
import webapp2
import jinja2
import datetime

import time # for delay
import random

from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), "templates")
JINJA_ENVIRONMENT  = jinja2.Environment(
                loader = jinja2.FileSystemLoader(template_dir),
                autoescape = True)

class Activity(ndb.Model):
    activity_name =  ndb.StringProperty()
    repetition_rate = ndb.IntegerProperty()
    dates_done = ndb.PickleProperty()
    date_added = ndb.DateTimeProperty(auto_now_add=True)


def populate ():
    activity = Activity(activity_name = "do dishes", dates_done=[datetime.datetime.today()])
    activity.put()
    time.sleep(.1)

def get_activities():
    activities = Activity.query().order(Activity.date_added).fetch()
    if not activities:
        populate()
        activities = Activity.query().order(Activity.date_added).fetch()

    color_codes = {
        0: "lightblue",
        1: "lightviolet",
        2: "salmon",
        3: "orange",
        4: "red",
        5: "brown"
    }

    for activity in activities:
        activity.urgency = color_codes[random.randint(0,5)]
        # todo: change with actual nums from time difference

    template_values = {
        "today" : datetime.datetime.today(),
        #todo : get int out of time difference
        "activities" : activities,
    }

    return template_values

def get_template_values(template):

    get_values_function_mapper = {
        "days_since": get_activities,
    }

    if template in get_values_function_mapper:
        return get_values_function_mapper[template]()

    return {}

def add_new(page):
    activity_name = page.request.get('new')
    activity = Activity(
        activity_name = activity_name,
        dates_done = [datetime.datetime.today()]
    )

    activity.put()
    time.sleep(.1)

def add_date(page):
    activity_key = page.request.get('activity_key')
    activity = ndb.Key('Activity', int(activity_key)).get()
    activity.dates_done.append(datetime.datetime.today())
    activity.put()
    time.sleep(.1)


def make_post(page, function):
    post_function_mapper = {
        "add_new": add_new,
        "days_since": add_date,
    }

    if function in post_function_mapper:
        post_function_mapper[function](page)


class Page(webapp2.RequestHandler):

    def get(self, reg_input="index"):

        template_values = get_template_values(reg_input)
        html_template = reg_input + ".html"

        template = JINJA_ENVIRONMENT.get_template(html_template)
        self.response.write(template.render(template_values))


    def post(self, reg_input="index"):

        make_post(self, reg_input)
        self.redirect('/' + reg_input)

app = webapp2.WSGIApplication([(r'/', Page), ('/(\w+)', Page)], debug = True)
