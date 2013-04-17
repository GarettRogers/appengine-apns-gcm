import json
import logging
import time
import uuid
from google.appengine.api import memcache
from google.appengine.ext import ndb

class GcmToken(ndb.Model):
    gcm_token = ndb.StringProperty(indexed=True)
    enabled = ndb.BooleanProperty(indexed=True, default=True)
    registration_date = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

class GcmTags(ndb.Model):
    token = ndb.KeyProperty(kind=GcmToken, repeated=True)
    tag = ndb.StringProperty(indexed=True, required=True)

