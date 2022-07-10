from concret.config.configuration import Configuration
from concret.constant import *

from concret.exception import CustomeException
from concret.logger import logging
import sys

from concret.entity.config_entity import DataIngestionConfig
from concret.entity.artifact_entity import DataIngestionArtifact
from concret.component.data_ingestion import DataIngestion



class Pipeline:

    def __init__(self,config:Configuration=Configuration())->None:
         ## creating and passing Configuration() class object
        
        try:
            self.config=config ## self.config is -> Configuration() class object
                               ## This objectcan be used throughout Pipeline() class as self.config
        except Exception as e:
            raise CustomeException(e,sys) from e


    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            ## Get data_ingestion_config config details from Configuration() class (coded in configuration.py)
            data_ingestion=DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())
            
            ## Pass above fetched configuration data to DataIngestion() class coded in component>data_ingestion.py
            ## data_ingestion is object of DataIngestion()
            return data_ingestion.initiate_data_ingestion()

        except Exception as e:
            raise CustomeException(e,sys) from e 

    def start_data_validation(self):
        pass

    def start_data_transformation(self):
        pass    

    def start_mdoel_trainer(self):
        pass 

    def start_model_evaluation(self):
        pass  

    def start_model_pusher(self):
        pass  

    def run_pipeline(self):
        try:
            ## Calling function/method under this pipeline.py / pipeline() class start_data_ingestion()
            data_ingestion_artifact=self.start_data_ingestion()

        except Exception as e:
            raise CustomeException(e,sys) from e
