from concret.config.configuration import Configuration
from concret.constant import *

from concret.exception import CustomException
from concret.logger import logging
import sys

from concret.entity.config_entity import DataIngestionConfig,DataValidationConfig,ModelEvaluationConfig
from concret.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,ModelTrainerArtifact,ModelPusherArtifact,ModelEvaluationArtifact
from concret.component.data_ingestion import DataIngestion
from concret.component.data_validation import DataValidation
from concret.component.data_transformation import DataTransformation
from concret.component.model_trainer import ModelTrainer
from concret.component.model_evaluation import ModelEvaluation

import mlflow


class Pipeline:

    def __init__(self,config:Configuration=Configuration())->None:
         ## creating and passing Configuration() class object
        
        try:
            self.config=config ## self.config is -> Configuration() class object
                               ## This objectcan be used throughout Pipeline() class as self.config
        except Exception as e:
            raise CustomException(e,sys) from e


    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            ## Get data_ingestion_config config details from Configuration() class (coded in configuration.py)
            data_ingestion=DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())
            
            ## Pass above fetched configuration data to DataIngestion() class coded in component>data_ingestion.py
            ## data_ingestion is object of DataIngestion()
            return data_ingestion.initiate_data_ingestion()

        except Exception as e:
            raise CustomException(e,sys) from e 

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) \
            -> DataValidationArtifact:
        try:
            data_validation = DataValidation(data_validation_config=self.config.get_data_validation_config(),
                                             data_ingestion_artifact=data_ingestion_artifact)

            return data_validation.initiate_data_validation()
        except Exception as e:
            raise CustomException(e,sys) from e

    def start_data_transformation(self,
                                  data_ingestion_artifact: DataIngestionArtifact,
                                  data_validation_artifact: DataValidationArtifact
                                  ) -> DataTransformationArtifact:
        try:
            data_transformation = DataTransformation(
                data_transformation_config=self.config.get_data_transformation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            return data_transformation.initiate_data_transformation()
        except Exception as e:
            raise CustomException(e, sys)    

    def start_model_trainer(self, 
                            data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            model_trainer = ModelTrainer(model_trainer_config=self.config.get_model_trainer_config(),
                                         data_transformation_artifact=data_transformation_artifact
                                         )
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise CustomException(e,sys) from e


    def start_model_evaluation(self, data_ingestion_artifact: DataIngestionArtifact,
                               data_validation_artifact: DataValidationArtifact,
                               model_trainer_artifact: ModelTrainerArtifact) -> ModelEvaluationArtifact:
        try:
            model_eval = ModelEvaluation(
                model_evaluation_config=self.config.get_model_evaluation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact,
                model_trainer_artifact=model_trainer_artifact)
            return model_eval.initiate_model_evaluation()
        except Exception as e:
            raise CustomException(e,sys) from e

    def start_model_pusher(self):
        pass  

    def run_pipeline(self):
        try:
            ## Calling function/method under this pipeline.py / pipeline() class start_data_ingestion()
            data_ingestion_artifact=self.start_data_ingestion()
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_ingestion_artifact=data_ingestion_artifact,
                                                                          data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.start_model_trainer(data_transformation_artifact)
            
            model_evaluation_artifact = self.start_model_evaluation(data_ingestion_artifact=data_ingestion_artifact,
                                                                    data_validation_artifact=data_validation_artifact,
                                                                    model_trainer_artifact=model_trainer_artifact)
            
        
        except Exception as e:
            raise CustomException(e,sys) from e
