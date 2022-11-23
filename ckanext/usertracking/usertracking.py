# encoding: utf-8

import datetime
import logging
from sqlalchemy import Table, Column, types, ARRAY, select, func, and_, desc, asc
from sqlalchemy.sql import text
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
import math
import datetime


import ckan.plugins as p
import ckan.model as model

log = logging.getLogger(__name__)

# need Primary Key for model so use below 'table(name)' instead
user_activity_tracker = Table(u"user_activity_tracker", model.meta.metadata,
    Column(u"id", types.UnicodeText, primary_key=True),
    Column(u"name", types.UnicodeText),
    Column(u"organisations", ARRAY(types.UnicodeText)),
    Column(u"page", types.UnicodeText),
    Column(u"seconds_on_page", types.SMALLINT),
    Column(u'timestamp', types.TIMESTAMP, primary_key=True)
)

init_cursor = "9999999"
row_limit = 2
page_table_limit = 3
org_table_limit = 2

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

# TODO: Pagination

class UserTrackingDAO(model.DomainObject):

    ####################################
    # Page engagement table operations #
    ####################################

    @classmethod
    def page_engagement_tracking(cls, searched_page, time_range, page, limit=page_table_limit):

        user_activity_tracker = table('user_activity_tracker')

        sql = select(
            [
                user_activity_tracker.c.page,
                func.count(user_activity_tracker.c.id.distinct()),
                func.sum(user_activity_tracker.c.seconds_on_page).label("secs")
            ]
        ).where(
            and_(
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                func.lower(user_activity_tracker.c.page).contains(searched_page.lower())
            )
        ).group_by(
            user_activity_tracker.c.page
        ).order_by(
            desc("secs")
        ).offset(
            (page-1)*limit
        ).limit(limit)

        print("\nPage offset: ",(page-1)*limit)

        page_engagement = model.Session.execute(sql).fetchall()

        return page_engagement, len(page_engagement)

    def page_engagement_tracking_size(cls, searched_page, time_range):
        user_activity_tracker = table('user_activity_tracker')

        sql = select(
            [
                func.count(user_activity_tracker.c.page.distinct())
            ]
        ).where(
            and_(
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                func.lower(user_activity_tracker.c.page).contains(searched_page.lower())
            )
        )

        page_engagement = model.Session.execute(sql).fetchall()

        return math.ceil(page_engagement[0][0]/page_table_limit)

    ############################################
    # Organisation engagement table operations #
    ############################################

    @classmethod
    def org_engagement_tracking(cls, searched_org, time_range, page, limit=org_table_limit):

        user_activity_tracker = table('user_activity_tracker')

        # if searched_org != "":
        #     contains = "{"+searched_org.lower()+"}"
        # else:
        #     contains = "{}"

        sql = select(
            [
                func.unnest(user_activity_tracker.c.organisations).label("org").distinct(),
                func.count(user_activity_tracker.c.id.distinct()),
                func.sum(user_activity_tracker.c.seconds_on_page).label("secs")
            ]
        ).where(
            and_(
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                # user_activity_tracker.c.organisations.contains(contains)
            )
        ).group_by(
            text("org")
        ).order_by(
            desc("secs")
        ).offset((page-1)*limit).limit(limit)

        print("\n"+str(sql)+"\n")

        org_engagement = model.Session.execute(sql).fetchall()

        # get rid non-searched orgs
        i = 0
        while i < len(org_engagement):
            if searched_org not in org_engagement[i][0]:
                org_engagement.pop(i)
            else:
                i+=1

        return org_engagement, len(org_engagement)

    def org_engagement_tracking_size(cls, searched_org, time_range):
        user_activity_tracker = table('user_activity_tracker')


        sql = select(
            [
                func.unnest(user_activity_tracker.c.organisations).label("org").distinct()
            ]
        ).where(
            and_(
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                # user_activity_tracker.c.organisations.contains(contains)
            )
        )

        org_engagement = model.Session.execute(sql).fetchall()

        # get rid non-searched orgs
        i = 0
        while i < len(org_engagement):
            if searched_org not in org_engagement[i][0]:
                org_engagement.pop(i)
            else:
                i+=1

        return math.ceil(len(org_engagement)/org_table_limit)
    
    ####################################
    # User engagement table operations #
    ####################################


    @classmethod
    def user_engagement_tracking(cls, searched_user, time_range, prev_cursor, next_cursor, direction, limit=row_limit):

        user_activity_tracker = table('user_activity_tracker')

        # print("\nDirection PreSQL:", direction)
        # print("\nPrev Cursor PreSQL:", prev_cursor)
        # print("\nNext Cursor PreSQL:", next_cursor)

        if direction == "fordward":
            cursor = next_cursor
            comparison = "<="
            order_by = desc("mins")
        elif direction == "backward":
            cursor = prev_cursor
            comparison = ">"
            order_by = asc("mins")
        else:
            cursor = next_cursor = init_cursor
            direction = "fordward"
            comparison = "<="
            order_by = desc("mins")

        sql = select(
            [
                user_activity_tracker.c.id,
                user_activity_tracker.c.name,
                func.max(user_activity_tracker.c.organisations),
                (func.sum(user_activity_tracker.c.seconds_on_page)/60).label("mins"),
            ]
        ).where(
            and_(
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                func.lower(user_activity_tracker.c.name).contains(searched_user.lower()),
            )
        ).group_by(
            user_activity_tracker.c.id,
            user_activity_tracker.c.name
        ).order_by(
            order_by
        ).having(
            text("sum(user_activity_tracker.seconds_on_page)/60"+comparison+" "+cursor)
        ).limit(limit+1) # gets 1 more row for cursor

        print("\nSQL: ",sql,"\n")

        user_engagement = model.Session.execute(sql).fetchall()
        
        # Update cursors
        if len(user_engagement) > 0:
        
            if direction == "fordward":

                # defines prev cursor if after first page
                if next_cursor != init_cursor:
                    prev_cursor = str(user_engagement[0][3])
                else:
                    prev_cursor = ""
    
                # define next cursor if there is more rows
                if len(user_engagement) > limit:
                    next_cursor = str(user_engagement[-1][3])
                else:
                    next_cursor = ""

            elif direction == "backward":
                # to counter order by
                user_engagement.reverse()

                next_cursor = prev_cursor

                # define prev cursor if there is more rows
                if len(user_engagement) > limit:
                    prev_cursor = str(user_engagement[1][3])
                else:
                    prev_cursor = ""

        else:
            prev_cursor = ""
            next_cursor = ""

        # print("\nDirection PostQL:", direction)
        # print("\nPrev Cursor PostSQL:", prev_cursor)
        # print("\nNext Cursor PostSQL:", next_cursor)

        return user_engagement[:limit], len(user_engagement[:limit]), prev_cursor, next_cursor, direction

# model.meta.mapper(UserTrackingDAO, user_activity_tracker)
