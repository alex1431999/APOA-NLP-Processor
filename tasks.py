"""
This module defines all the Celery tasks which this processor can execute.
It also runs all the setup required for celery to function.
"""
import os

from celery import Celery
from common.utils.logging import DEFAULT_LOGGER, LogTypes
from common.mongo.data_types.crawling.crawl_result import CrawlResult
from common.celery import queues

from helpers.decorators import inject_controller

app = Celery('tasks',
    broker = os.environ['BROKER_URL']
)

@app.task(name='process-crawl', queue=queues['processor'])
@inject_controller
def process_crawl(crawl_dict, controller=None):
    """
    Process a single crawl result

    :param dict crawl_dict: The dictonary of the crawl result
    :param Controller controller: The controller is injected by @inject_controller
    """
    crawl = CrawlResult.from_dict(crawl_dict)

    if not crawl:
        DEFAULT_LOGGER.log('Received empty crawl to process', log_type=LogTypes.ERROR.value)
        return None

    DEFAULT_LOGGER.log('Received processing reqeust for {} ({})'.format(crawl.keyword_string, crawl.language), log_type=LogTypes.INFO.value)
    
    result = controller.run_single_crawl(crawl)

    return True if result else False
