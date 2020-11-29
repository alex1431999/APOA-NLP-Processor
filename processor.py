"""
This module provides the processor to process gathered data using googles NLP
"""

import re

from google.cloud import language
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from common.utils.logging import DEFAULT_LOGGER, LogTypes
from common.utils.read_json import read_json

VADER_SUPPORTED_LANGUAGES = ["en"]

class GoogleCloudLanguageProcessor:
    """
    Google Cloud Language API proccessor
    You can find the credentials in the /secrets
    Make sure you set the credentials as an env var before you use this class
    """

    # Class attributes
    entity_types = read_json('./config/entity_types.json')
    entity_blacklist = read_json('./config/entity_blacklist.json')

    def __init__(self):
        """
        Establish a connection to the Google Cloud Language API Server
        """
        self.client = language.LanguageServiceClient()
        self.vader_analyzer = SentimentIntensityAnalyzer()
        DEFAULT_LOGGER.log('Connected to Google Cloud Language API', log_type=LogTypes.INFO.value)

    def entity_filter(self, entity, keyword_string):
        """
        A filter to check if an entity should be stored or not

        :param Entity entity: The entity which is supposed to be chekced
        :param str keyword_string: The keyword which was used to get the entity

        :return: If you should remove the entity
        :rtype: boolean
        """
        if entity.name.lower() == keyword_string.lower():
            return True
        
        if entity.name.lower() in self.entity_blacklist:
            return True

        if len(entity.name) == 1:
            return True

        return False

    def filter_entities(self, entities, keyword_string):
        """
        Execute `entity_filter` on each entity and remove all entities which don't pass the check

        :param List<Entity> entities: The entities which is supposed to be chekced
        :param str keyword_string: The keyword which was used to get the entity

        :return: All entities which pass the filter check
        :rtype: list
        """
        entities_filtered = []
        for entity in entities:
            if not self.entity_filter(entity, keyword_string):
                entities_filtered.append(entity)
        return entities_filtered

    def process(self, text: str, keyword_string: str, keyword_language: str):
        """
        Analyze given text and return the score returned by the API

        :return: Score, entities and categories
        :rtype: Tuple with 3 slots
        """
        # Clean text before inserting https://stackoverflow.com/questions/43358857/how-to-remove-special-characters-except-space-from-a-file-in-python/43358965
        text = re.sub(r"[^a-zA-Z0-9]+", ' ', text)

        # Setup
        document = language.types.Document(
            content=text,
            type=language.enums.Document.Type.PLAIN_TEXT
        )

        # Requests
        DEFAULT_LOGGER.log('Analyzing text: {}'.format(text), log_type=LogTypes.INFO.value)
        try: # Get the sentiment of the text
            if keyword_language in VADER_SUPPORTED_LANGUAGES:
                score = self.vader_analyzer.polarity_scores("this is a very positive sentence PogU")["compound"]
            else:
                score = self.client.analyze_sentiment(document=document).document_sentiment.score
        except Exception as ex: # If it fails make document sentiment None
            DEFAULT_LOGGER.log('Failed to get sentiment of {}'.format(keyword_string), LogTypes.ERROR.value, ex)
            score = None

        try: # Get all entities of the text
            entities = self.client.analyze_entity_sentiment(document=document).entities
            entities = self.filter_entities(entities, keyword_string)
        except Exception as ex: # If it fails make entities an empty list
            DEFAULT_LOGGER.log('Failed to get entities of {}'.format(keyword_string), LogTypes.ERROR.value, ex)
            entities = []

        try: # Get the categories of the text
            categories = self.client.classify_text(document=document).categories
        except Exception as ex: # If it fails make categories an empty list
            DEFAULT_LOGGER.log('Failed to get categories for {}'.format(keyword_string), LogTypes.ERROR.value, ex)
            categories = []
        
        return (score, entities, categories)
