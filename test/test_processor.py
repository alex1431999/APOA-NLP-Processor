"""
This module tests all relevant functionality of the processor
"""

import unittest

from unittest.mock import patch, MagicMock

from processor import GoogleCloudLanguageProcessor, VADER_SUPPORTED_LANGUAGES

class GoogleCloudClientMock():
    """
    This class is a mock version of the
    API object that is returned after logging
    into the Google Cloud
    """
    def __init__(self):
        """
        Adjust any of the values below to change the output of the corresponding functions
        """
        # Sentiment default response
        self.sentiment_document_object = SentimentDocument(1)

        # Entity default response
        self.entities = [Entity("test")]

        # Category default response
        self.categories = ["/test"]

    """
    These response fixtures are declared as function so that you only
    need to adjust the attributes like `entities` for example to change the
    entire response.
    """
    @property
    def sentiment_object(self):
        return Sentiment(self.sentiment_document_object)

    @property
    def entity_sentiment_object(self):
        return EntitySentiment(self.entities)

    @property
    def category_response_object(self):
        return CategoryResponse(self.categories)

    def analyze_sentiment(self, document=None):
        return self.sentiment_object

    def analyze_entity_sentiment(self, document=None):
        return self.entity_sentiment_object

    def classify_text(self, document=None):
        return self.category_response_object

class Sentiment():
    """
    This class is a simplified version of the sentiment class used by the google library
    """
    def __init__(self, document_sentiment):
        self.document_sentiment = document_sentiment

class SentimentDocument():
    """
    This class is a simplified version of the sentiment document class used by the google library
    """
    def __init__(self, score):
        self.score = score

class EntitySentiment():
    """
    This class is a simplified version of the entitiy sentiment class used by the google library
    """
    def __init__(self, entities):
        self.entities = entities

class Entity():
    """
    This class is a simplified version of the entity class used by the google library
    """
    def __init__(self, name):
        self.name = name

class CategoryResponse():
    """
    This class is a simplified version of the category response class used by the google library
    """
    def __init__(self, categories):
        self.categories = categories

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
        self.google_cloud_mock = patch("processor.language.LanguageServiceClient", return_value=self.google_cloud_client_mock_object)
        self.google_cloud_mock.start()

    def test_construction(self):
        processor = GoogleCloudLanguageProcessor()
        self.assertIsNotNone(processor)

    def test_api_connection(self):
        client = self.processor.client
        self.assertIsNotNone(client)

    def test_entity_filter_passing(self):
        entity = Entity("test")
        self.processor.entity_blacklist = [] # Remove any potentially blacklisted entities

        result = self.processor.entity_filter(entity, "keyword")
        self.assertFalse(result, "Entity should have not been filtered")

    def test_entity_filter_name(self):
        name = "some name"
        entity = Entity(name)
        self.processor.entity_blacklist = [] # Remove any potentially blacklisted entities

        result = self.processor.entity_filter(entity, name)
        self.assertTrue(result, "Entity should have been filtered")

    def test_entity_filter_blacklist(self):
        entity_blacklisted = Entity("test")
        self.processor.entity_blacklist = [entity_blacklisted.name]

        result = self.processor.entity_filter(entity_blacklisted, "keyword")
        self.assertTrue(result, "Entity should have been filtered")

    def test_entity_filter_entity_length(self):
        entity = Entity("t")
        self.assertEqual(len(entity.name), 1, "Make sure the entities name is of length 1")
        self.processor.entity_blacklist = [] # Remove any potentially blacklisted entities

        result = self.processor.entity_filter(entity, "keyword")
        self.assertTrue(result, "Entity should have been filtered")

    def test_process_passing(self):
        result = self.processor.process("some text", "keyword", "zh")
        self.assertIsNotNone(result, "The function should have returned something")

    def test_process_results_not_none(self):
        score, entities, categories = self.processor.process("some text", "keyword", "zh")

        self.assertIsNotNone(score, "There should be a score")
        self.assertIsNotNone(entities, "There should be entities")
        self.assertIsNotNone(categories, "There should be categories")

    def test_process_results_content(self):
        score_expected = self.google_cloud_client_mock_object.sentiment_document_object.score
        entities_expected = self.google_cloud_client_mock_object.entities
        categories_expected = self.google_cloud_client_mock_object.categories

        score, entities, categories = self.processor.process("some text", "keyword", "zh")

        self.assertEqual(score, score_expected)
        self.assertEqual(entities, entities_expected)
        self.assertEqual(categories, categories_expected)

    @patch("processor.SentimentIntensityAnalyzer.polarity_scores", mock=MagicMock(return_value={ "compound": 15 }))
    def test_process_vader_used(self, mock):
        language = VADER_SUPPORTED_LANGUAGES[0]
        
        self.processor.process("some text", "keyword", language)

        self.assertTrue(mock.called)

    @patch("processor.SentimentIntensityAnalyzerGerman.polarity_scores", mock=MagicMock(return_value={"compound": 15}))
    def test_process_vader_used_german(self, mock):
        language = "de"

        self.processor.process("some text", "keyword", language)

        self.assertTrue(mock.called)
