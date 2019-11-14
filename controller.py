"""
Module to hanlde different scripts that the crawler can execute
"""

from common.mongo.data_types.keyword import Keyword

from processor import GoogleCloudLanguageProcessor

class Controller():
    """
    Hanldes the different scripts and order of execution
    """
    def __init__(self):
        """
        Initialise the Processor
        """
        self.processor = GoogleCloudLanguageProcessor()
