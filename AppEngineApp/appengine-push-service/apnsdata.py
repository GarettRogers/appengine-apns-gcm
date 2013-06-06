import json
import logging
import time
import uuid
from google.appengine.api import memcache
from google.appengine.ext import ndb

class ApnsToken(ndb.Model):
    apns_token = ndb.StringProperty(indexed=True)
    enabled = ndb.BooleanProperty(indexed=True, default=True)
    registration_date = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

class ApnsSandboxToken(ndb.Model):
    apns_token = ndb.StringProperty(indexed=True)
    enabled = ndb.BooleanProperty(indexed=True, default=True)
    registration_date = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

class ApnsTag(ndb.Model):
    token = ndb.KeyProperty(kind=ApnsToken)
    tag = ndb.StringProperty(indexed=True, required=True)

class ApnsSandboxTag(ndb.Model):
    token = ndb.KeyProperty(kind=ApnsSandboxToken)
    tag = ndb.StringProperty(indexed=True, required=True)

