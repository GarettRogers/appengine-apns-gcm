import json
import logging
import time
import uuid
from google.appengine.api import memcache
from google.appengine.ext import ndb

class AppConfig(ndb.Model):
    gcm_api_key = ndb.StringProperty()
    gcm_multicast_limit = ndb.IntegerProperty()
    apns_multicast_limit = ndb.IntegerProperty()
    apns_test_mode = ndb.BooleanProperty()
    apns_sandbox_cert = ndb.TextProperty()
    apns_sandbox_key = ndb.TextProperty()
    apns_cert = ndb.TextProperty()
    apns_key = ndb.TextProperty()
    