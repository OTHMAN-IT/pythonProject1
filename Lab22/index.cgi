#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from pythonProject1 import app

CGIHandler().run(app)