"""
Module to hanlde different scripts that the crawler can execute

Google NLP Quota:
Link: https://cloud.google.com/natural-language/automl/quotas
"The current usage quotas for AutoML Natural Language are 600 prediction requests per minute per project 
and 600 non-prediction requests per minute per project. These quotas apply collectively to all deployed models."
"""

import os
import time

from threading import Thread

from common.mongo.controller import MongoController
from common.utils.logging import DEFAULT_LOGGER, LogTypes

from processor import GoogleCloudLanguageProcessor

class Controller():
    """
    Hanldes the different scripts and order of execution
    """
    def __init__(self):
        """
        Initialise the Processor
        """
        self.MAX_REQUESTS_PER_MIN = 600 / 3 # 600 requests per minute, each process sends 3 requests

        # Mongo
        mongo_connection_string = os.environ['MONGO_CONNECTION_STRING']
        mongo_db_name = os.environ['MONGO_DB_NAME']

        self.processor = GoogleCloudLanguageProcessor()
        self.mongo_controller = MongoController(mongo_connection_string, mongo_db_name)

    def __process_crawl(self, crawl):
        """
        Process a crawl result

        :param CrawlResult crawl: The to be processed crawl result
        """
        keyword = self.mongo_controller.get_keyword_by_id(crawl.keyword_ref, cast=True)

        score, entities, categories = self.processor.process(crawl.text, crawl.keyword_string)

        entities_formatted = []
        for entity in entities:
            entity = {"value": entity.name, "score": entity.sentiment.score, "count": 1}
            new_entity = True

            for entity_already_included in entities_formatted:
                if entity_already_included["value"] == entity["value"]:
                    entity_already_included["count"] += entity["count"]
                    new_entity = False

            if new_entity:
                entities_formatted.append(entity)

        categories_formatted = []
        for category in categories:
            category = {"value": category.name, "confidence": category.confidence, "count": 1}
            new_category = True

            for category_already_included in categories_formatted:
                if category_already_included["value"] == category["value"]:
                    category_already_included["count"] += category["count"]
                    new_category = False

            if new_category:
                categories_formatted.append(category)

        self.mongo_controller.set_entities_crawl(crawl._id, entities_formatted)
        self.mongo_controller.set_categories_crawl(crawl._id, categories_formatted)

        if score:
            return self.mongo_controller.set_score_crawl(crawl._id, score)
        return None

    def run_single_crawl(self, crawl):
        """
        Process a single input crawl

        :param CrawlResult crawl: The to be processed crawl result
        """
        return self.__process_crawl(crawl)
    
    def run_full(self):
        """
        Fetch all crawls which have to be processed and process them in batches of MAX_REQUESTS_AT_ONCE
        """
        crawls = ['Placeholder']

        while crawls:
            threads = []
            crawls = self.mongo_controller.get_unprocessed_crawls(self.MAX_REQUESTS_PER_MIN, cast=True)

            for crawl in crawls:
                thread = Thread(target=self.__process_crawl, args=(crawl,))
                thread.start()
                threads.append(thread)
                
            for thread in threads:
                thread.join()

            DEFAULT_LOGGER.log('Sleeping for one minute...', log_type=LogTypes.INFO.value)
            time.sleep(60) # Ensure that the quota limit is not being exceeded
            
