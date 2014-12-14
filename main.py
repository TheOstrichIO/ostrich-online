# Copyright 2014 The Ostrich | by Itamar Ostricher

"""Ostrich Online GAE main module"""

import cgi
import json
import logging
import lxml.html
import re
import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import models

class SocialStatsFetcherBase(webapp2.RequestHandler):
    """Social stats fetcher base class."""

    def fetch_page(self, echo_page=False, test_data=False):
        """Return content HTML of page from URL property.

        @param  echo_page   Pass True to write fetched page to response
        @param  test_data   Pass True to "fetch" from test data instead
        """
        self.response.write('<div>Fetching %s</div>' % (self.url))
        content_html = None
        if test_data:
            with open(self.url) as html_file:
               content_html = html_file.read()
        else:
            result = urlfetch.fetch(self.url, headers={'Accept-Language': 'en'})
            self.response.write('<div>Fetch result status code: %d</div>' %
                                (result.status_code))
            if 200 == result.status_code:
                content_html = result.content
        if echo_page and content_html:
            self.response.write('<div>%s</div>' % (cgi.escape(content_html)))
        return content_html

    def xpath_analyzer(self, content_html):
        """Use XPath to extract stats, and return stats dictionary."""
        html = lxml.html.fromstring(content_html)
        stats = dict()
        for stat_name, selector in self.stats_map.iteritems():
            stat_block = html.find(self.xpath_search_str % (selector))
            assert stat_block is not None
            logging.debug('%s: %s', stat_name, stat_block.text_content())
            stats[stat_name] = int(stat_block.text_content().replace(',', ''))
        return stats

    def get(self):
        """Fetch stats page from URL property and analyze page."""
        content_html = self.fetch_page()        
        if content_html:
            stats = self.extract_stats(content_html)
            logging.debug('Stats from %s: %r', self.url, stats)
            self.response.write('<div>%s</div>' % (json.dumps(stats)))
            if stats:
                stats_record = self.StatsRecord(**stats)
                stats_record.put()
        else:
            self.response.write('<div>Fetch URL %s failed</div>' % (self.url))

class TwitterFetcher(SocialStatsFetcherBase):
    @property
    def url(self):
        """URL to fetch"""
        return u'https://twitter.com/OstricherIO'
        # test data URL: 'test-data/twitter.com/OstricherIO.html'

    @property
    def StatsRecord(self):
        """Stats record model type"""
        return models.TwitterStats

    @property
    def stats_map(self):
        """Dictionary of extracted stats and their XPath paths"""
        return {
            'tweets': 'ProfileNav-item--tweets is-active',
            'following': 'ProfileNav-item--following',
            'followers': 'ProfileNav-item--followers',
            'favorites': 'ProfileNav-item--favorites',
        }

    @property
    def xpath_search_str(self):
        return ('.//li[@class="ProfileNav-item %s"]/a/'
                'span[@class="ProfileNav-value"]')

    def extract_stats(self, content_html):
        """Return stats dictinoary."""
        return self.xpath_analyzer(content_html)

class FacebookFetcher(SocialStatsFetcherBase):
    @property
    def url(self):
        """URL to fetch"""
        return u'https://www.facebook.com/Ostrich.IO'
        # test data URL: 'test-data/twitter.com/OstricherIO.html'

    @property
    def StatsRecord(self):
        """Stats record model type"""
        return models.FacebookStats

    def extract_stats(self, content_html):
        """Return stats dictinoary."""
        stats = dict()
        meta_match = re.search(r'\<meta\s+name\=\"description\"\s+content'
                               '\=\"([^\"]+)\"', content_html)
        if meta_match:
            meta_desc = meta_match.group(1)
            logging.debug('meta description: %s', meta_desc)
            likes_match = re.search(r'(\d+)\s+likes', meta_desc)
            if likes_match:
                stats['likes'] = int(likes_match.group(1))
            else:
                logging.error('Failed matching likes count')
            talks_match = re.search(r'(\d+)\s+talking', meta_desc)
            if talks_match:
                stats['talks'] = int(talks_match.group(1))
            else:
                logging.error('Failed matching talking count')
        else:
            logging.error('Failed meta-match RegEx')
        return stats

class GooglePlusFetcher(SocialStatsFetcherBase):
    @property
    def url(self):
        """URL to fetch"""
        return u'https://plus.google.com/u/0/+OstricherIO/about'
        # test data: 'test-data/plus.google.com/Ostricher.IO_about.gae.html'

    @property
    def StatsRecord(self):
        """Stats record model type"""
        return models.GooglePlusStats

    @property
    def stats_map(self):
        """Dictionary of extracted stats and their XPath paths"""
        return {
            'followers': '1',
            'views': 'last()',
        }

    @property
    def xpath_search_str(self):
        return './/div[@class="Zmjtc"]/span[%s]'

    def extract_stats(self, content_html):
        """Return stats dictinoary."""
        return self.xpath_analyzer(content_html)

# Create routes.
ROUTES = [webapp2.Route(r'/fetch/twitter', TwitterFetcher),
          webapp2.Route(r'/fetch/facebook', FacebookFetcher),
          webapp2.Route(r'/fetch/gplus', GooglePlusFetcher)]

# Instantiate the webapp2 WSGI application.
APP = webapp2.WSGIApplication(ROUTES, debug=True)
