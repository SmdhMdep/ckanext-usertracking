import datetime
import pytest

from ckan import model
from ckan.tests import factories

from ckanext.usertracking.usertracking import UserTracking


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
        rows, count = UserTracking.page_engagement_tracking('','24')
        assert (rows, count) == ([], 0)

    def test_org_engagement_tracking(self):
        user_page_access = UserTracking.org_engagement_tracking('','24')
        assert user_page_access == ([], 0)

    def test_user_engagement_tracking(self):
        user_activity = UserTracking.user_engagement_tracking('','1')
        assert user_activity == ([], 0)
