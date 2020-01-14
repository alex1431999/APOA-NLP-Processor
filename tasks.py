"""
This module defines all the Celery tasks which this processor can execute.
It also runs all the setup required for celery to function.
"""
import os

from celery import Celery
from common.utils.logging import DEFAULT_LOGGER, LogTypes
from common.mongo.data_types.crawling.crawl_result import CrawlResult
from common.celery import queues

from controller import Controller

app = Celery('tasks',
    broker = os.environ['BROKER_URL']
)

controller = Controller()

@app.task(name='process-crawl', queue=queues['processor'])
def process_crawl(crawl_dict):
    """
    Process a single crawl result

    :param dict crawl_dict: The dictonary of the crawl result
    """
    crawl = CrawlResult.from_dict(crawl_dict)

    if not crawl:
        DEFAULT_LOGGER.log('Received empty crawl to process', log_type=LogTypes.ERROR.value)
        return None

    DEFAULT_LOGGER.log('Received processing reqeust for {} ({})'.format(crawl.keyword_string, crawl.language), log_type=LogTypes.INFO.value)
