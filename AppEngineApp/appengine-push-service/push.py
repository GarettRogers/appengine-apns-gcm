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

#TODO:
# - Make this more fail safe -- use Backends and a Task Queue or something so that we can guarantee delivery, and so it doesn't tie up the request when we are broadcasting to a very large number of devices
# - Properly handle feedback from the APNS Feedback service

def convertToGcmMessage(self, message):
    gcmmessage = {}
    gcmmessage["data"] = {}
    
    if 'android_collapse_key' in message["request"]:
        gcmmessage["collapse_key"] = message["request"]["android_collapse_key"]
    
    if 'data' in message["request"]:
        gcmmessage["data"] = message["request"]["data"]

    return gcmmessage

def convertToApnsMessage(self, message):
    apnsmessage = {}
    apnsmessage["data"] = {}
    apnsmessage["sound"] = "default"
    apnsmessage["badge"] = -1
    apnsmessage["alert"] = None
    apnsmessage["custom"] = None
    
    if 'ios_sound' in message["request"]:
        apnsmessage["sound"] = message["request"]["ios_sound"]
    
    if 'data' in message["request"]:
        apnsmessage["custom"] = message["request"]["data"]

    if 'ios_badge' in message["request"]:
        apnsmessage["badge"] = message["request"]["ios_badge"]

    if 'ios_message' in message["request"] and 'ios_button_text' in message["request"]:
        apnsmessage["alert"] = PayloadAlert(message["request"]["ios_message"], action_loc_key=message["request"]["ios_button_text"])
    else:
        if 'ios_message' in message["request"]:
            apnsmessage["alert"] = message["request"]["ios_message"]
    
    return apnsmessage

def getAPNs():
    appconfig = AppConfig.get_or_insert("config")
    
    if appconfig.apns_test_mode:
        return APNs(use_sandbox=True, cert_file=appconfig.apns_sandbox_cert, key_file=appconfig.apns_sandbox_key)
    else:
        return APNs(use_sandbox=False, cert_file=appconfig.apns_cert, key_file=appconfig.apns_key)

def GetApnsToken(regid):
    appconfig = AppConfig.get_or_insert("config")
    if appconfig.apns_test_mode:
        return ApnsSandboxToken.get_or_insert(regid)
    else:
        return ApnsToken.get_or_insert(regid)

def sendMulticastApnsMessage(self, apns_reg_ids, apnsmessage):
    apns = getAPNs()
    
    # Send a notification
    payload = Payload(alert=apnsmessage["alert"], sound=apnsmessage["sound"], custom=apnsmessage["custom"], badge=apnsmessage["badge"])
    apns.gateway_server.send_notifications(apns_reg_ids, payload)

    # Get feedback messages
    for (token_hex, fail_time) in apns.feedback_server.items():
        break

def sendSingleApnsMessage(self, message, token):
    apns_reg_ids=[token]
    sendMulticastApnsMessage(self, apns_reg_ids, message)


def sendMulticastGcmMessage(self, gcm_reg_ids, gcmmessage):
    appconfig = AppConfig.get_or_insert("config")
    gcm = GCM(appconfig.gcm_api_key)

    # JSON request
    response = gcm.json_request(registration_ids=gcm_reg_ids, data=gcmmessage)
    if 'errors' in response:
        for error, reg_ids in response['errors'].items():
            # Check for errors and act accordingly
            if error is 'NotRegistered':
                # Remove reg_ids from database
                for reg_id in reg_ids:
                    token = GcmToken.get_or_insert(reg_id)
                    token.key.delete()
    
    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].items():
            # Repace reg_id with canonical_id in your database
            token = GcmToken.get_or_insert(reg_id)
            token.key.delete()
            
            token = GcmToken.get_or_insert(canonical_id)
            token.gcm_token = canonical_id
            token.enabled = True
            token.put()


def sendSingleGcmMessage(self, message, token):
    gcm_reg_ids=[token]
    sendMulticastGcmMessage(self, gcm_reg_ids, message)

def broadcastGcmMessage(self, message):
    appconfig = AppConfig.get_or_insert("config")
    gcmmessage = message
    
    gcm_reg_ids = []
    q = GcmToken.query(GcmToken.enabled == True)
    x=0
    
    for token in q.iter():
        if x == appconfig.gcm_multicast_limit:
            sendMulticastGcmMessage(self, gcm_reg_ids, gcmmessage)
            gcm_reg_ids.clear()
            x = 0
        
        gcm_reg_ids.append(token.gcm_token)
        x = x + 1
    
    if len(gcm_reg_ids) > 0:
        sendMulticastGcmMessage(self, gcm_reg_ids, gcmmessage)


def broadcastApnsMessage(self, message):
    appconfig = AppConfig.get_or_insert("config")
    apnsmessage = message
    
    apns_reg_ids = []
    if appconfig.apns_test_mode:
        q = ApnsSandboxToken.query(ApnsSandboxToken.enabled == True)
    else:
        q = ApnsToken.query(ApnsToken.enabled == True)

    x=0
    
    for token in q.iter():
        if x == appconfig.apns_multicast_limit:
            sendMulticastApnsMessage(self, apns_reg_ids, apnsmessage)
            apns_reg_ids.clear()
            x = 0
        
        apns_reg_ids.append(token.apns_token)
        x = x + 1
    
    if len(apns_reg_ids) > 0:
        sendMulticastApnsMessage(self, apns_reg_ids, apnsmessage)


#Sample POST Data -->  message={"request":{"data":{"custom": "json data"},"platforms": [1,2], "ios_message":"This is a test","ios_button_text":"yeah!","ios_badge": -1, "ios_sound": "soundfile", "android_collapse_key": "collapsekey"}}
class BroadcastMessage(webapp2.RequestHandler):
    def post(self):
        msg = json.loads(self.request.get("message"))
        if 1 in msg["request"]["platforms"]:
            #Send to Android devices using GCM
            broadcastGcmMessage(self, convertToGcmMessage(self, msg))
    
        if 2 in msg["request"]["platforms"]:
            #Send to iOS devices using APNS
            broadcastApnsMessage(self, convertToApnsMessage(self, msg))

        #Return result
        self.response.write("OK")

class BroadcastMessageToTag(webapp2.RequestHandler):
    def post(self):
        msg = json.loads(self.request.get("message"))
        if 1 in msg["request"]["platforms"]:
            tagid = self.request.get("tagid")
            
            q = GcmTag.query(GcmTag.tag == tagid)
            for tag in q.iter():
                sendSingleGcmMessage(self, convertToGcmMessage(self, msg), tag.token.get().gcm_token)
    
        if 2 in msg["request"]["platforms"]:
            #Send to iOS devices using APNS
            tagid = self.request.get("tagid")
            
            q = ApnsSandboxTag.query(ApnsSandboxTag.tag == tagid)
            for tag in q.iter():
                sendSingleApnsMessage(self, convertToApnsMessage(self, msg), tag.token.get().apns_token)
            
        #Return result
        self.response.write("OK")


#Sample POST Data -->  platform=1&token=<device token string>&message={"request":{"data":{"custom": "json data"}, "ios_message":"This is a test","ios_button_text":"yeah!","ios_badge": -1, "ios_sound": "soundfile", "android_collapse_key": "collapsekey"}}
class SendMessage(webapp2.RequestHandler):
   def post(self):
        platform = self.request.get("platform")
        message = self.request.get("message")
        token = self.request.get("token")
        
        #Send a single message to a device token
        if platform == "1": #Android
            sendSingleGcmMessage(convertToGcmMessage(self, json.loads(message)), token)
        elif platform == "2": #iOS
            sendSingleApnsMessage(convertToApnsMessage(self, json.loads(message)), token)
                
        self.response.write("OK")

app = webapp2.WSGIApplication([
    ('/push/tagbroadcast', BroadcastMessageToTag),
    ('/push/broadcast', BroadcastMessage),
    ('/push/send', SendMessage)
], debug=True)
