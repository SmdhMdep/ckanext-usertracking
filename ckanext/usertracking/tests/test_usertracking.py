import datetime
import pytest

from ckan import model
from ckan.tests import factories

from ckanext.usertracking.usertracking import UserTrackingDAO
import sqlalchemy as sa

@pytest.mark.ckan_config('ckan.plugins', 'usertracking')
@pytest.mark.usefixtures("with_plugins", "with_request_context")
@pytest.mark.usefixtures("clean_db")
class TestUsertrackingPlugin(object):

    @pytest.fixture(autouse=True)
    def initial_data(self, clean_db, with_request_context):
        engine = sa.create_engine("postgresql://ckan_default:J0o2eDRChOtE@127.0.0.1:5432/ckan_test")
        dummyData = [["bbbd2457-4071-40bc-af88-5b84d895d419","ckan-admin5",["sme4"],"/dataset/b",10],["bbbd2457-4071-40bc-af88-5b84d895d418","ckan-admin4",["sme3"],"/dataset",10],["bbbd2457-4071-40bc-af88-5b84d895d417","ckan-admin2",["sme1"],"/dataset",3], ["00000000-0000-0000-0000-000000000000","ckan-admin3",["sme2"],"/dataset/a",3] ]
        for data in dummyData:
            sql = '''INSERT INTO user_activity_tracker
                    (id, name, organisations, page, seconds_on_page)
                    VALUES (%s, %s, %s, %s, %s)'''
            engine.execute(sql, data[0], data[1], data[2], data[3], data[4])
        pass
    
    def test_page_engagement_tracking(self):
        rows = UserTrackingDAO.page_engagement_tracking('','24',1)
        assert rows == [('/dataset', 2, 13), ('/dataset/b', 1, 10), ('/dataset/a', 1, 3)]

    def test_org_engagement_tracking(self):
        user_page_access = UserTrackingDAO.org_engagement_tracking('','24',1)
        assert user_page_access == [('sme3', 1, 10), ('sme4', 1, 10), ('sme1', 1, 3), ('sme2', 1, 3)]

    def test_user_engagement_tracking(self):
        user_activity = UserTrackingDAO.user_engagement_tracking('','1',1)
        assert user_activity == [('bbbd2457-4071-40bc-af88-5b84d895d418', 'ckan-admin4', ['sme3'], 10), ('bbbd2457-4071-40bc-af88-5b84d895d419', 'ckan-admin5', ['sme4'], 10), ('00000000-0000-0000-0000-000000000000', 'ckan-admin3', ['sme2'], 3), ('bbbd2457-4071-40bc-af88-5b84d895d417', 'ckan-admin2', ['sme1'], 3)]