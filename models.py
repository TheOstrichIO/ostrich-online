# Copyright 2014 The Ostrich | by Itamar Ostricher

"""Ostrich Online GAE Models module"""

from google.appengine.ext import ndb

class TwitterStats(ndb.Model):
    """Twitter stats record"""
    api_level = ndb.IntegerProperty(default=0)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    followers = ndb.IntegerProperty()
    following = ndb.IntegerProperty()
    tweets = ndb.IntegerProperty()
    favorites = ndb.IntegerProperty()

class FacebookStats(ndb.Model):
    """Facebook stats record"""
    api_level = ndb.IntegerProperty(default=0)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    likes = ndb.IntegerProperty()
    talks = ndb.IntegerProperty()

class GooglePlusStats(ndb.Model):
    """Google+ stats record"""
    api_level = ndb.IntegerProperty(default=0)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    followers = ndb.IntegerProperty()
    views = ndb.IntegerProperty()
