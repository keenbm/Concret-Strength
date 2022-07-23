from collections import namedtuple
from datetime import datetime
import uuid
from threading import Thread
from typing import List
from multiprocessing import Process

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
from concret.component.model_pusher import ModelPusher
import mlflow

import os, sys
from collections import namedtuple
from datetime import datetime
import pandas as pd
from concret.constant import EXPERIMENT_DIR_NAME, EXPERIMENT_FILE_NAME

# Named Tupled storing Experiment Logs
Experiment = namedtuple("Experiment", ["experiment_id", "initialization_timestamp", "artifact_time_stamp",
                                       "running_status", "start_time", "stop_time", "execution_time", "message",
                                       "experiment_file_path", "accuracy", "is_model_accepted"])

class Pipeline(Thread):
    # Inhereting Thread calss in Pipeline class()
    # Threading Help in parallel execution of code
    # Training of code and GUI can run simalteniously
    experiment: Experiment = Experiment(*([None] * 11))
    experiment_file_path = None

    def __init__(self,config:Configuration)->None:
         ## Need to Pass Configuration() class object to whever Pipeline() class is called
        
        try:
            # Creating file for storing Experiment related data
            os.makedirs(config.training_pipeline_config.artifact_dir, exist_ok=True)
            Pipeline.experiment_file_path=os.path.join(config.training_pipeline_config.artifact_dir,EXPERIMENT_DIR_NAME, EXPERIMENT_FILE_NAME)
            
            # Inhereting methods of Thread class
            super().__init__(daemon=False, name="pipeline")
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

    def start_model_pusher(self, model_eval_artifact: ModelEvaluationArtifact) -> ModelPusherArtifact:
        try:
            model_pusher = ModelPusher(
                model_pusher_config=self.config.get_model_pusher_config(),
                model_evaluation_artifact=model_eval_artifact
            )
            return model_pusher.initiate_model_pusher()
        except Exception as e:
            raise CustomException(e,sys) from e


    def run_pipeline(self):
        try:
            # If Pipeline is already running , thn dont start new pipeline (Training process)
            if Pipeline.experiment.running_status:
                logging.info("Pipeline is already running")
                return Pipeline.experiment
            logging.info("Pipeline starting.")

            # Generating Unique ID for each experiment /Pipeline run
            experiment_id = str(uuid.uuid4())

            # Storing Experiment data in named Tupled before Pipeline is started
            Pipeline.experiment = Experiment(experiment_id=experiment_id,
                                             initialization_timestamp=self.config.time_stamp,
                                             artifact_time_stamp=self.config.time_stamp,
                                             running_status=True,
                                             start_time=datetime.now(),
                                             stop_time=None,
                                             execution_time=None,
                                             experiment_file_path=Pipeline.experiment_file_path,
                                             is_model_accepted=None,
                                             message="Pipeline has been started.",
                                             accuracy=None,
                                             )
            logging.info(f"Pipeline experiment: {Pipeline.experiment}")

            self.save_experiment()

            
            
            
            ## Calling function/method under this pipeline.py / pipeline() class start_data_ingestion()
            data_ingestion_artifact=self.start_data_ingestion()
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_ingestion_artifact=data_ingestion_artifact,
                                                                          data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.start_model_trainer(data_transformation_artifact)
            
            model_evaluation_artifact = self.start_model_evaluation(data_ingestion_artifact=data_ingestion_artifact,
                                                                    data_validation_artifact=data_validation_artifact,
                                                                    model_trainer_artifact=model_trainer_artifact)
            

            ## If Model is acceptable after evaluation thn Copy/Pusg model in Saved model directory
            ## Saved Model folder is created dynamically ModelPusher() in root directory
            ## Acceptable model = Better thn previous Best model & Better than base accuracy defined
            if model_evaluation_artifact.is_model_accepted:
                model_pusher_artifact = self.start_model_pusher(model_eval_artifact=model_evaluation_artifact)
                logging.info(f'Model pusher artifact: {model_pusher_artifact}')
            else:
                logging.info("Trained model rejected.")
            
            
            
            logging.info("Pipeline completed.")
            stop_time = datetime.now()

            # Storing Experiment data in named Tupled After Pipeline completes
            Pipeline.experiment = Experiment(experiment_id=Pipeline.experiment.experiment_id,
                                             initialization_timestamp=self.config.time_stamp,
                                             artifact_time_stamp=self.config.time_stamp,
                                             running_status=False,
                                             start_time=Pipeline.experiment.start_time,
                                             stop_time=stop_time,
                                             execution_time=stop_time - Pipeline.experiment.start_time,
                                             message="Pipeline has been completed.",
                                             experiment_file_path=Pipeline.experiment_file_path,
                                             is_model_accepted=model_evaluation_artifact.is_model_accepted,
                                             accuracy=model_trainer_artifact.model_accuracy
                                             )
            logging.info(f"Pipeline experiment: {Pipeline.experiment}")
            self.save_experiment()
        except Exception as e:
            raise CustomException(e, sys) from e



             
    def run(self):
    ## run function needs to be defined when we use Threding
    ## Here Thread class is inherated by pipeline class
    ## Whenever Pipeline.start() is called , this function will be executed
    # An this will execute main pipeline function -- > self.run_pipeline()
        try:
            self.run_pipeline()
        except Exception as e:
            raise e




    def save_experiment(self):
        try:
            if Pipeline.experiment.experiment_id is not None:
                experiment = Pipeline.experiment
                experiment_dict = experiment._asdict()
                experiment_dict: dict = {key: [value] for key, value in experiment_dict.items()}

                experiment_dict.update({
                    "created_time_stamp": [datetime.now()],
                    "experiment_file_path": [os.path.basename(Pipeline.experiment.experiment_file_path)]})

                experiment_report = pd.DataFrame(experiment_dict)

                os.makedirs(os.path.dirname(Pipeline.experiment_file_path), exist_ok=True)
                if os.path.exists(Pipeline.experiment_file_path):
                    experiment_report.to_csv(Pipeline.experiment_file_path, index=False, header=False, mode="a")
                else:
                    experiment_report.to_csv(Pipeline.experiment_file_path, mode="w", index=False, header=True)
            else:
                print("First start experiment")
        
        except Exception as e:
            raise CustomException(e,sys) from e



    @classmethod
    def get_experiments_status(cls, limit: int = 5) -> pd.DataFrame:
        try:
            if os.path.exists(Pipeline.experiment_file_path):
                df = pd.read_csv(Pipeline.experiment_file_path)
                limit = -1 * int(limit)
                return df[limit:].drop(columns=["experiment_file_path", "initialization_timestamp"], axis=1)
            else:
                return pd.DataFrame()
        except Exception as e:
            raise CustomException(e, sys) from e