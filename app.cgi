#! /usr/bin/env python3

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/users/anthonyn/public_html/cis322/htbin/proj5-mongo/env/lib/python3.4/site-packages")

import cgitb
cgitb.enable()

from wsgiref.handlers import CGIHandler
from main import app

CGIHandler().run(app)
