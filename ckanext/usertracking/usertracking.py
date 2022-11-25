# encoding: utf-8

import datetime
from sqlalchemy import Table, Column, types, ARRAY, select, func, and_, desc
from sqlalchemy.sql import text
import math
import datetime

import ckan.plugins as p
import ckan.model as model

# need Primary Key for model to use funciton 'table(name)' 
# instead used compound PK but not reflective of DB
# this model might be useful for testing
user_activity_tracker = Table(u"user_activity_tracker", model.meta.metadata,
    Column(u"id", types.UnicodeText, primary_key=True),
    Column(u"name", types.UnicodeText),
    Column(u"organisations", ARRAY(types.UnicodeText)),
    Column(u"page", types.UnicodeText),
    Column(u"seconds_on_page", types.SMALLINT),
    Column(u'timestamp', types.TIMESTAMP, primary_key=True)
)

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

# Contains all the usertracking tables queries
class UserTrackingDAO(model.DomainObject):

    page_row_limit = 50

    #################################
    # Page engagement table queries #
    #################################

    @classmethod
    def page_engagement_tracking(cls, searched_page, time_range, page, limit=page_row_limit):

        user_activity_tracker = table('user_activity_tracker')

        sql = select(
                [
                    user_activity_tracker.c.page,
                    func.count(user_activity_tracker.c.id.distinct()),
                    func.sum(user_activity_tracker.c.seconds_on_page).label("secs")
                ]
            ).where(
                and_(
                    # exclude non-logged users
                    # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000",
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

        page_engagement = model.Session.execute(sql).fetchall()

        return page_engagement


    def page_engagement_tracking_size(cls, searched_page, time_range, limit=page_row_limit):

        user_activity_tracker = table('user_activity_tracker')

        sql = select(
                [
                    func.count(user_activity_tracker.c.page.distinct())
                ]
            ).where(
                and_(
                    # exclude non-logged users
                    # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000",
                    user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                    func.lower(user_activity_tracker.c.page).contains(searched_page.lower())
                )
            )

        page_engagement = model.Session.execute(sql).fetchall()

        return page_engagement[0][0], math.ceil(page_engagement[0][0]/limit)

    #########################################
    # Organisation engagement table queries #
    #########################################

    @classmethod
    def org_engagement_tracking(cls, searched_org, time_range, page, limit=page_row_limit):

        user_activity_tracker = table('user_activity_tracker')

        # Because of the unnesting of the organisations column,
        # it is necessary to use a nested query for the WHERE clause for string searching
        general_sql = select(
                [
                    func.unnest(user_activity_tracker.c.organisations).label("org"),
                    func.count(user_activity_tracker.c.id.distinct()),
                    func.sum(user_activity_tracker.c.seconds_on_page).label("secs")
                ]
            ).where(
                and_(
                    # exclude non-logged users
                    # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000", 
                    user_activity_tracker.c.timestamp > 
                        (datetime.datetime.now() - datetime.timedelta(hours=int(time_range)))
                )
            ).group_by(
                text("org")
            ).alias("unnested_orgs")

        search_sql = select(['*']).select_from(general_sql).where(
            func.lower(general_sql.c.org).contains(searched_org.lower())
            ).order_by(
                desc(general_sql.c.secs)
            ).offset(
                (page-1)*limit
            ).limit(limit)

        org_engagement = model.Session.execute(search_sql).fetchall()

        return org_engagement


    def org_engagement_tracking_size(cls, searched_org, time_range, limit=page_row_limit):
        user_activity_tracker = table('user_activity_tracker')

        # Because of the unnesting of the organisations column,
        # it is necessary to use a nested query for the WHERE clause for string searching
        general_sql = select(
                [
                    func.unnest(user_activity_tracker.c.organisations).distinct().label("org")
                ]
            ).where(
                and_(
                    # exclude non-logged users
                    # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000"
                    user_activity_tracker.c.timestamp > 
                        (datetime.datetime.now() - datetime.timedelta(hours=int(time_range)))
                )
            ).alias("unnested_orgs")
            
        search_sql = select([func.count('*')]).select_from(general_sql).where(
                func.lower(general_sql.c.org).contains(searched_org.lower())
            )

        org_engagement = model.Session.execute(search_sql).fetchall()

        return org_engagement[0][0], math.ceil(org_engagement[0][0]/limit)


    #################################
    # User engagement table queries #
    #################################

    @classmethod
    def user_engagement_tracking(cls, searched_user, time_range, page, limit=page_row_limit):

        user_activity_tracker = table('user_activity_tracker')

        sql = select(
            [
                user_activity_tracker.c.id,
                user_activity_tracker.c.name,
                func.max(user_activity_tracker.c.organisations),
                func.sum(user_activity_tracker.c.seconds_on_page).label("secs"),
            ]
        ).where(
            and_(
                # exclude non-logged users
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000",
                user_activity_tracker.c.timestamp > (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                func.lower(user_activity_tracker.c.name).contains(searched_user.lower()),
            )
        ).group_by(
            user_activity_tracker.c.id,
            user_activity_tracker.c.name
        ).order_by(
            desc("secs")
        ).offset(
            (page-1)*limit
        ).limit(limit)

        user_engagement = model.Session.execute(sql).fetchall()

        return user_engagement


    def user_engagement_tracking_size(cls, searched_user, time_range, limit=page_row_limit):

        user_activity_tracker = table('user_activity_tracker')

        sql = select(
            [
                func.count(user_activity_tracker.c.id.distinct())
            ]
        ).where(
            and_(
                # exclude non-logged users
                # user_activity_tracker.c.id != "00000000-0000-0000-0000-000000000000",
                user_activity_tracker.c.timestamp > 
                    (datetime.datetime.now() - datetime.timedelta(hours=int(time_range))),
                func.lower(user_activity_tracker.c.name).contains(searched_user.lower()),
            )
        )

        user_engagement = model.Session.execute(sql).fetchall()

        return user_engagement[0][0], math.ceil(user_engagement[0][0]/limit)

model.meta.mapper(UserTrackingDAO, table('user_activity_tracker'))