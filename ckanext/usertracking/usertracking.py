# encoding: utf-8

import datetime
import logging
from sqlalchemy import Table, Column, types, ARRAY, select, func, and_, desc
from sqlalchemy.sql import text
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()

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

# class UserActivityTracker(Base):
#     __tablename__ = u"user_activity_tracker"
#     id = Column(types.UnicodeText)
#     name = Column(types.UnicodeText)
#     organisations = Column(ARRAY(types.UnicodeText))
#     page = Column(types.UnicodeText)
#     seconds_on_page = Column(types.SMALLINT)
#     timestamp = Column(types.TIMESTAMP)

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

# TODO: Pagination
class UserTrackingDAO(model.DomainObject):

    @classmethod
    def page_engagement_tracking(cls, searched_page, time_range, limit=500):

        user_activity_tracker = table('user_activity_tracker')

        sql = select(
            [
                user_activity_tracker.c.page,
                func.count(user_activity_tracker.c.id.distinct()),
                (func.sum(user_activity_tracker.c.seconds_on_page)/60).label("mins")
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
            desc("mins")
            # desc(func.sum(user_activity_tracker.c.seconds_on_page))
        ).limit(limit)

        page_engagement = model.Session.execute(sql).fetchall()

        return page_engagement, len(page_engagement)


    @classmethod
    def org_engagement_tracking(cls, searched_org, time_range, limit=500):

        user_activity_tracker = table('user_activity_tracker')

        # if searched_org != "":
        #     contains = "{"+searched_org.lower()+"}"
        # else:
        #     contains = "{}"

        sql = select(
            [
                func.unnest(user_activity_tracker.c.organisations).label("org").distinct(),
                func.count(user_activity_tracker.c.id.distinct()),
                (func.sum(user_activity_tracker.c.seconds_on_page)/60).label("mins")
            ]
        ).where(
            and_(
                user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                # user_activity_tracker.c.organisations.contains(contains)
            )
        ).group_by(
            text("org")
        ).order_by(
            desc("mins")
        ).limit(limit)

        org_engagement = model.Session.execute(sql).fetchall()

        # get rid non-searched orgs
        i = 0
        while i < len(org_engagement):
            if searched_org not in org_engagement[i][0]:
                org_engagement.pop(i)
            else:
                i+=1


        return org_engagement, len(org_engagement)


    @classmethod
    def user_engagement_tracking(cls, searched_user, time_range, cursor, next, limit=2):

        user_activity_tracker = table('user_activity_tracker')

        if next == "true":
            comparison = "<"
        else:
            comparison = ">"

        sql = select(
            [
                user_activity_tracker.c.id,
                user_activity_tracker.c.name,
                func.max(user_activity_tracker.c.organisations),
                (func.sum(user_activity_tracker.c.seconds_on_page)/60).label("mins"),
            ]
        ).where(
            and_(
                user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", # non-logged users
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                func.lower(user_activity_tracker.c.name).contains(searched_user.lower()),
            )
        ).group_by(
            user_activity_tracker.c.id,
            user_activity_tracker.c.name
        ).order_by(
            desc("mins")
            # desc(func.sum(user_activity_tracker.c.seconds_on_page))
        ).having(
            text("sum(user_activity_tracker.seconds_on_page)/60"+comparison+" "+cursor)
        ).limit(limit)


        print("\nSQL: ",sql,"\n")
        print("\n Bef C:",cursor,"\n")
        print("\nNext S:",next,"\n")

        user_engagement = model.Session.execute(sql).fetchall()

        if len(user_engagement) > 0:
            cursor = str(user_engagement[-1][3])
        else:
            cursor = 9999999
        print("\nAfter C:",cursor,"\n")

        return user_engagement, len(user_engagement), cursor, next

model.meta.mapper(UserTrackingDAO, user_activity_tracker)
