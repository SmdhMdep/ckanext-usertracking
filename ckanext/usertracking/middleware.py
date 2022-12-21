import hashlib
from logging import log
import uuid

import six
from six.moves.urllib.parse import unquote

import sqlalchemy as sa

from ckan.plugins import toolkit

import os
import logging
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

log = logging.getLogger(__name__)

class UsertrackingMiddleware(object):

    def __init__(self, app, config):
        self.app = app
        self.engine = sa.create_engine(config.get('sqlalchemy.url'))

    def __call__(self, environ, start_response):
        
        path = environ['PATH_INFO']
        method = environ.get('REQUEST_METHOD')

        if path == '/_usertracking' and method == 'POST':
            log.info("\nPOST INCOMING: New usetracking middleware working great yaay!!\n")

            #Send response, reduces wait time if at top
            start_response('200 OK', [('Content-Type', 'text/html')])

            #get user ID
            #if user is not logged in give a a set UUID
            try:
                id = uuid.UUID(environ["webob._parsed_post_vars"][0]["id"])
            except:
                id = "00000000-0000-0000-0000-000000000000"

            #if user is not logged in give a a set name
            try:
                name = environ["webob._parsed_post_vars"][0]["name"]
            except:
                name = "guest"

            time = int(float(environ["webob._parsed_post_vars"][0]["time"]))

            try:
                url = environ["webob._parsed_post_vars"][0]["url"]
            except:
                url = "/"
            
            # Fix to once in a blue moon issue
            # Database uses SMALLINT, so if time is more than 32768, it will cause a problem
            if time > 32000:
                time = 32000

            # Get orgs based on userID and format them in a list
            formattedOrgs = []
            try:
                orgs = toolkit.get_action('organization_list_for_user')({'ignore_auth': True}, {"id": str(id)})
                for org in orgs:
                    formattedOrgs.append(org["name"])
            except:
                # If get orgs dont work they are a guest
                formattedOrgs.append("guest")
                name = "guest"

            # Send data to database
            sql = '''INSERT INTO user_activity_tracker
                    (id, name, organisations, page, seconds_on_page)
                    VALUES (%s, %s, %s, %s, %s)'''
            self.engine.execute(sql, id, name, formattedOrgs, url, time)
                
            return []
        return self.app(environ, start_response)
