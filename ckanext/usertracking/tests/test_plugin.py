import unittest
from unittest.mock import patch
import ckanext.usertracking.plugin as plugin
import ckanext.usertracking as usertracking
from mock import MagicMock, DEFAULT
from flask import Blueprint
from parameterized import parameterized
import pytest

class PluginTest(unittest.TestCase):

    def setUp(self):
        # Create mocks
        self._tk = plugin.toolkit
        plugin.toolkit = MagicMock()

        self._usertracking_lib = plugin.usertracking
        plugin.usertracking_lib = MagicMock()

        # Create the plugin
        self.usertracking = plugin.UsertrackingPlugin()


    def tearDown(self):
        plugin.tk = self._tk
        plugin.usertracking_lib = self._usertracking_lib


    @parameterized.expand([
        (plugin.plugins.IConfigurer,),
        (plugin.plugins.IBlueprint,)
    ])
    def test_implementation(self, interface):
        self.assertTrue(interface.implemented_by(plugin.UsertrackingPlugin))


    def test_get_blueprint(self):
        # Call the method
        self.assertIsInstance(self.usertracking.get_blueprint(), Blueprint)


    def test_update_config(self):
        
        config = {}
        self.usertracking.update_config(config)

        plugin.toolkit.add_template_directory.assert_called_once_with(config, u'templates')
        plugin.toolkit.add_public_directory(config, u'public')
        plugin.toolkit.add_resource(u'public/ckanext/usertracking', u'ckanext_usertracking')
        plugin.toolkit.add_ckan_admin_tab(config, 'usertracking.admin/usertracking', 'Engagement tracking',
            'ckan.admin_tabs', 'bar-chart-o')


    @patch("ckanext.usertracking.plugin.usertracking_view")
    def test_render(self, usertracking_view):

        response = plugin.usertracking_view()

        usertracking_view.assert_called_once()

        self.assertEqual(response, usertracking_view())