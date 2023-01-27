import datetime
import ckan.model as model

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types
from sqlalchemy import func
from ckan.model.meta import metadata,  mapper, Session
from ckan.model.types import make_uuid


#Schema of package_granular_visibility table
user_activity_tracker_mapping_table = Table('user_activity_tracker' , metadata,
    
    Column(u"id", types.UnicodeText, primary_key=True),
    Column(u"name", types.UnicodeText),
    Column(u"organisations", types.ARRAY(types.UnicodeText)),
    Column(u"page", types.UnicodeText),
    Column(u"seconds_on_page", types.SMALLINT),
    Column(u'timestamp', types.TIMESTAMP, primary_key=True,
        server_default=func.current_timestamp()
    ),
    extend_existing=True
)



#Commands that can be preformed on table
class user_activity_tracker_mapping(model.DomainObject):
    @classmethod
    def get(cls, **kw):
        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(**kw).first()

    @classmethod
    def get_all(cls, **kw):
        query = model.Session.query(cls).all()
        return query

    @classmethod
    def find(cls, **kw):
        query = model.Session.query(cls).autoflush(False)
        return query.filter_by(**kw)

model.meta.mapper(user_activity_tracker_mapping, user_activity_tracker_mapping_table)