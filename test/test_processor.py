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
