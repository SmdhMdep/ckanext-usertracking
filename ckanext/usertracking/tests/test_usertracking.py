import datetime
import pytest

from ckan import model
from ckan.tests import factories

from ckanext.usertracking.usertracking import UserTrackingDAO


@pytest.mark.ckan_config('ckan.plugins', 'usertracking')
@pytest.mark.usefixtures("with_plugins", "with_request_context")
@pytest.mark.usefixtures("clean_db")
class TestUsertrackingPlugin(object):

    @pytest.mark.usefixtures("clean_db")
    def test_migrations_applied(self, migrate_db_for):
        migrate_db_for("usertracking")
        assert model.Session.bind.has_table("user_activity_tracker")

    @pytest.fixture(autouse=True)
    def initial_data(self, clean_db, with_request_context):
        # TODO: Add dummy data for the rest of tests
        pass
    
    def test_page_engagement_tracking(self):
        rows, count = UserTrackingDAO.page_engagement_tracking('','24')
        # TODO: Modify assert to contain relevant dummy data
        assert (rows, count) == ([], 0)

    def test_org_engagement_tracking(self):
        user_page_access = UserTrackingDAO.org_engagement_tracking('','24')
        # TODO: Modify assert to contain relevant dummy data
        assert user_page_access == ([], 0)

    def test_user_engagement_tracking(self):
        user_activity = UserTrackingDAO.user_engagement_tracking('','1')
        # TODO: Modify assert to contain relevant dummy data
        assert user_activity == ([], 0)
