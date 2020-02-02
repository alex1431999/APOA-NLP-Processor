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

from common.mongo.data_types.keyword import Keyword
from common.mongo.controller import MongoController
from common.neo4j.controller import Neo4jController
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

        # Neo4J
        neo_connection_string = os.environ['NEO_CONNECTION_STRING']
        neo_user = os.environ['NEO_USER']
        neo_password = os.environ['NEO_PASSWORD']

        self.processor = GoogleCloudLanguageProcessor()
        self.mongo_controller = MongoController(mongo_connection_string, mongo_db_name)
        self.neo_controller = Neo4jController(neo_connection_string, neo_user, neo_password)

    def __process_crawl(self, crawl):
        """
        Process a crawl result

        :param CrawlResult crawl: The to be processed crawl result
        """
        keyword = self.mongo_controller.get_keyword_by_id(crawl.keyword_ref, cast=True)

        score, entities, categories = self.processor.process(crawl.text, crawl.keyword_string)

        self.neo_controller.add_keyword(keyword)

        for entity in entities:
            self.neo_controller.add_entity(entity.name, keyword.language, entity.sentiment.score, 1, keyword._id)

        for category in categories:
            self.neo_controller.add_category(category.name, keyword.language, category.confidence, 1, keyword._id)

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
            
