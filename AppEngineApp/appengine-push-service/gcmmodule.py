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

class GCMRegister(webapp2.RequestHandler):
    def post(self):
        regid = self.request.get("regId")
        if not regid:
            self.response.out.write('Must specify regid')
        else:
            token = GcmToken.get_or_insert(regid)
            token.gcm_token = regid
            token.enabled = True
            token.put()

class GCMUnregister(webapp2.RequestHandler):
    def post(self):
        regid = self.request.get("regId")
        token = GcmToken.get_or_insert(regid)
        token.enabled = False
        token.put()

class GCMTagHandler(webapp2.RequestHandler):
    def post(self):
        tagid = self.request.get("tagid")
        regid = self.request.get("regid")
        
        appconfig = AppConfig.get_or_insert("config")
        
        token = GcmToken.get_or_insert(regid)
        tag = GcmTag.get_or_insert(tagid + regid, tag=tagid, token=token.key)
    
    
    def delete(self):
        tagid = self.request.get("tagid")
        regid = self.request.get("regid")
        
        appconfig = AppConfig.get_or_insert("config")
        
        tag = GcmTag.get_or_insert(tagid + regid)
        tag.key.delete()

app = webapp2.WSGIApplication([
    ('/gcm/tag', GCMTagHandler),
    ('/gcm/register', GCMRegister),
    ('/gcm/unregister', GCMUnregister)
], debug=True)
