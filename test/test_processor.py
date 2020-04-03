"""
This module tests all relevant functionality of the processor
"""

import unittest

from unittest.mock import patch

from processor import GoogleCloudLanguageProcessor

class GoogleCloudClientMock():
    """
    This class is a mock version of the
    API object that is returned after logging
    into the Google Cloud
    """
    def __init__(self):
        pass

class Entity():
    """
    This class is a simplified version of the entity class used by the google library
    """
    def __init__(self, name):
        self.name = name

class TestGoogleCloudLanguageProcessor(unittest.TestCase):
    """
    Testing Setup
    """
    def setUp(self):
        # Mocking
        self.google_cloud_client_mock_object = GoogleCloudClientMock()
        self.mock_google_cloud_client()

        # Processor
        self.processor = GoogleCloudLanguageProcessor()

    def mock_google_cloud_client(self):
        self.google_cloud_mock = patch('google.cloud.language.LanguageServiceClient')
        self.google_cloud_mock.start()
        self.google_cloud_mock.return_value = self.google_cloud_client_mock_object

    def test_construction(self):
        processor = GoogleCloudLanguageProcessor()
        self.assertIsNotNone(processor)

    def test_api_connection(self):
        client = self.processor.client
        self.assertIsNotNone(client)

    def test_entity_filter_passing(self):
        entity = Entity('test')
        self.processor.entity_blacklist = [] # Remove any potentially blacklisted entities

        result = self.processor.entity_filter(entity, 'keyword')
        self.assertFalse(result, 'Entity should have not been filtered')

    def test_entity_filter_name(self):
        name = 'some name'
        entity = Entity(name)
        self.processor.entity_blacklist = [] # Remove any potentially blacklisted entities

        result = self.processor.entity_filter(entity, name)
        self.assertTrue(result, 'Entity should have been filtered')

    def test_entity_filter_blacklist(self):
        entity_blacklisted = Entity('test')
        self.processor.entity_blacklist = [entity_blacklisted.name]

        result = self.processor.entity_filter(entity_blacklisted, 'keyword')
        self.assertTrue(result, 'Entity should have been filtered')

    def test_entity_filter_entity_length(self):
        entity = Entity('t')
        self.assertEqual(len(entity.name), 1, 'Make sure the entities name is of length 1')
        self.processor.entity_blacklist = [] # Remove any potentially blacklisted entities

        result = self.processor.entity_filter(entity, 'keyword')
        self.assertTrue(result, 'Entity should have been filtered')
