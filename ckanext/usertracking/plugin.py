import csv
import datetime
from collections import namedtuple

import ckanext.usertracking.usertracking as usertracking
import ckanext.usertracking.middleware as usertracking_middleware

import click
from flask import Blueprint
import logging

import ckan.model as model
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import _

c = toolkit.c

_TrackingCount = namedtuple(u'TrackingCount', u'id name organisations page seconds_on_page timestamp')


# Used to render page in get_blueprint()
def usertracking_view():

    context = {'model': model, 'user': c.user, 'auth_user_obj': c.userobj}

    try:
        toolkit.check_access('sysadmin', context, {})
    except toolkit.NotAuthorized:
        return toolkit.abort(403, 'Need to be system administrator to administer')

    tracking = usertracking.UserTrackingDAO()

    extra_vars = {}
    extra_vars[u'q'] = search = toolkit.request.args.get(u'q', u'')


    # Page engagement (LIMIT OFFSET PAGINATION)
    pageTBLprefix =  u'page_engagement_'

    page_engagement_time_range = toolkit.request.args.get(pageTBLprefix+u'time_range', u'24')
    extra_vars[pageTBLprefix+u'time_range'] = page_engagement_time_range
    page_engagement_current = int(toolkit.request.args.get(pageTBLprefix+u'current', 1))
    page_engagement_total = tracking.page_engagement_tracking_size(
        searched_page=search, time_range=page_engagement_time_range)


    extra_vars[pageTBLprefix+u'table'], extra_vars[pageTBLprefix+u'count'] = tracking.page_engagement_tracking(
        searched_page=search, time_range=page_engagement_time_range, page=page_engagement_current)
    extra_vars[pageTBLprefix+u'current'] = page_engagement_current
    extra_vars[pageTBLprefix+u'total'] = page_engagement_total

    print("\nPage Current: ",page_engagement_current)
    print("\nPage Total: ",page_engagement_total)


    # Org. engagement (LIMIT OFFSET PAGINATION)
    orgTBLprefix = u'org_engagement_'

    org_engagement_time_range = toolkit.request.args.get(orgTBLprefix+u'time_range', u'168')
    org_engagement_current = int(toolkit.request.args.get(orgTBLprefix+u'current', 1))
    org_engagement_total = tracking.org_engagement_tracking_size(
        searched_org=search, time_range=org_engagement_time_range)

    print("\nOrg Current: ",org_engagement_current)
    print("\nOrg Total: ",org_engagement_total)

    extra_vars[orgTBLprefix+u'total'] = org_engagement_total
    extra_vars[orgTBLprefix+u'current'] = org_engagement_current
    extra_vars[orgTBLprefix+u'time_range'] = org_engagement_time_range
    extra_vars[orgTBLprefix+u'table'], extra_vars[orgTBLprefix+u'count'] = tracking.org_engagement_tracking(
    searched_org=search, time_range=org_engagement_time_range, page=org_engagement_current)


    # User engagement (CURSOR PAGINATION)
    userTBLprefix = u'user_engagement_'

    nc = toolkit.request.args.get(userTBLprefix+u'next_cursor', u'')
    pc = toolkit.request.args.get(userTBLprefix+u'prev_cursor', u'')
    dir = toolkit.request.args.get(userTBLprefix+u'direction', u'first')
    range = toolkit.request.args.get(userTBLprefix+u'time_range', u'168')

    tbl, count, pc, nc, dir = tracking.user_engagement_tracking(
        searched_user=search, time_range=range, prev_cursor=pc, next_cursor=nc, direction=dir)

    userTBL_vars = {
        userTBLprefix+u'table': tbl,
        userTBLprefix+u'count': count,
        userTBLprefix+u'next_cursor': nc,
        userTBLprefix+u'prev_cursor': pc,
        userTBLprefix+u'direction': dir,
        userTBLprefix+u'time_range': range
    }

    extra_vars.update(userTBL_vars)

    print("\nPrev Cursor TK: "+pc)
    # print("\nPrev Cursor vars: ",extra_vars[userTBLprefix+u'prev_cursor'])

    print("\nNext Cursor TK: "+nc)
    # print("\nNext Cursor vars: ",extra_vars[userTBLprefix+u'next_cursor'])

    print("\nNext TK: "+dir)
    # print("\nNext vars: ",extra_vars[userTBLprefix+u'direction'])

    return toolkit.render(u'admin/engagement_tracking_tab.html', extra_vars)


class UsertrackingPlugin(plugins.SingletonPlugin):
    u'''User tracking plugin.'''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IMiddleware)
    plugins.implements(plugins.IClick)

    #####################################################
    ############## Configurer INTERFACE #################
    #####################################################

    def update_config(self, config_):
        toolkit.add_template_directory(config_, u'templates')
        toolkit.add_public_directory(config_, u'public')
        toolkit.add_resource(u'public/ckanext/usertracking', u'ckanext_usertracking')
        toolkit.add_ckan_admin_tab(config_, 'usertracking.admin/usertracking', 'Engagement tracking',
            'ckan.admin_tabs', 'bar-chart-o')

    ####################################################
    ############## Blueprint INTERFACE #################
    ####################################################

    def get_blueprint(self):
        
        # Create Blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'

        # Add plugin url rules to Blueprint object
        rules = [
            (u'/ckan-admin/usertracking', u'admin/usertracking', usertracking_view)
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint


    ####################################################
    ############## MIDDLEWARE INTERFACE ################
    ####################################################

    def make_middleware(self, app, config):

        return usertracking_middleware.UsertrackingMiddleware(app, config)


    def make_error_log_middleware(self, app, config):

        return usertracking_middleware.UsertrackingMiddleware(app, config)


    #####################################################
    ############## CLICK (CLI) INTERFACE ################
    #####################################################
    def get_commands(self):

        def _user_tracking(engine, measure_from):
            sql = u'''
                SELECT * from user_activity_tracker WHERE timestamp >= %(measure_from)s
                ORDER BY timestamp DESC
            '''
            return [_TrackingCount(*t) for t in engine.execute(
                    sql, measure_from=str(measure_from)
                ).fetchall()
            ]

        def export_user_tracking(engine, output_filename, days):
            #start_date = datetime.datetime.strptime(start_date, u'%d-%m-%Y')

            u'''Write user tracking to a csv file.'''
            HEADINGS2 = [
                u'user id',
                u'user name',
                u'organisation/s',
                u'page',
                u'seconds on page',
                u'timestamp',
            ]

            measure_from = datetime.date.today() - datetime.timedelta(days=days)
            user_views = _user_tracking(engine, measure_from)

            with open(output_filename, u'w') as fh2:
                f_out = csv.writer(fh2)
                f_out.writerow(HEADINGS2)
                f_out.writerows([(r.id,
                                r.name,
                                r.organisations,
                                r.page,
                                r.seconds_on_page,
                                r.timestamp)
                            for r in user_views])
    
        @click.group(name=u'usertracking', short_help=u'User tracking statistics')
        def usertracking():
            pass

        @usertracking.command(short_help=u'Exports last fortnight user tracking data')
        @click.argument(u'output_file', type=click.Path())
        @click.option(u'--days', default=1, type=click.IntRange(1, 90), help="Number of days in the past included")
        # @click.argument(u'start_date', required=False, help="Start date of query in format %d-%m-%Y e.j. 02-10-2021")
        def export(output_file, days): #, start_date
            engine = model.meta.engine
            export_user_tracking(engine, output_file, days)

        return [usertracking, export]
