#!/usr/bin/env python
# appengine-apns-gcm was developed by Garett Rogers <garett.rogers@gmail.com>
# Source available at https://github.com/GarettRogers/appengine-apns-gcm
#
# appengine-apns-gcm is distributed under the terms of the MIT license.
#
# Copyright (c) 2013 AimX Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import webapp2
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from gcmdata import *
from gcm import *
from apns import *
from apnsdata import *
from appdata import *

appconfig = None

class ConfigureApp(webapp2.RequestHandler):
    def get(self):
        appconfig = AppConfig.get_or_insert("config")
        
        if not appconfig.gcm_api_key:
            appconfig.gcm_api_key = "<gcm key here>"
        if not appconfig.gcm_multicast_limit:
            appconfig.gcm_multicast_limit = 1000
        if not appconfig.apns_multicast_limit:
            appconfig.apns_multicast_limit = 1000
        if appconfig.apns_test_mode == None:
            appconfig.apns_test_mode = True
        if not appconfig.apns_sandbox_cert:
            appconfig.apns_sandbox_cert = "<sandbox pem certificate string>"
        if not appconfig.apns_sandbox_key:
            appconfig.apns_sandbox_key = "<sandbox pem private key string>"
        if not appconfig.apns_cert:
            appconfig.apns_cert = "<pem certificate string>"
        if not appconfig.apns_key:
            appconfig.apns_key = "<pem private key string>"
        
        appconfig.put()
        
        template_values = {
            'appconfig': appconfig,
        }
        path = os.path.join(os.path.dirname(__file__), 'config.html')
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        appconfig = AppConfig.get_or_insert("config")
        appconfig.gcm_api_key = self.request.get("gcm_api_key")
        appconfig.gcm_multicast_limit = int(self.request.get("gcm_multicast_limit"))
        appconfig.apns_multicast_limit = int(self.request.get("apns_multicast_limit"))
        appconfig.apns_sandbox_cert = self.request.get("apns_sandbox_cert")
        appconfig.apns_sandbox_key = self.request.get("apns_sandbox_key")
        appconfig.apns_cert = self.request.get("apns_cert")
        appconfig.apns_key = self.request.get("apns_key")
        
        if self.request.get("apns_test_mode") == "True":
            appconfig.apns_test_mode = True
        else:
            appconfig.apns_test_mode = False
        
        appconfig.put()
        
        template_values = {
            'appconfig': appconfig,
        }
        path = os.path.join(os.path.dirname(__file__), 'config.html')
        self.response.out.write(template.render(path, template_values))



app = webapp2.WSGIApplication([
    ('/admin/config', ConfigureApp)
], debug=True)
