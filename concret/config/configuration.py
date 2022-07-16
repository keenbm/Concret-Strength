import os


from shtab import DIR

## Importing entity (data structure created using named tupled)
from concret.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig,\
                           ModelTrainerConfig,ModelEvaluationConfig,ModelPusherConfig,TrainingPipelineConfig

## Importing YAML reader functions from
from concret.util.util import read_yaml_file

## Importing constans from constant module
from concret.constant import *

from concret.exception import CustomeException
from concret.logger import logging
import sys



class Configuration():
    '''
    Info:
    Configuration class is having Methods/Functions for fetching configuration details from YAML files and 
    returns entity (as per the named tuple defined in entity folder)
    Depedency for this calss : 
    - YAML file ready function mentioned in UTIL
    - NamedTuple skeleton mentioed in ENTITY folder
    - Variables mentioned in CONSTANT--> Based on this variable key, values from YAML file will be fetched

    '''

    def __init__(self,
                config_file_path:str=CONFIG_FILE_PATH,
                current_time_stamp:str=CURRENT_TIME_STAMP)->None: # CURRENT_TIME_STAMP,CONFIG_FILE_PATH is defined in CONSTANT module
        '''
        When configuration() class object is created , it'll read YAML file and get/fetch all configuration (entity/namedtuple) 
        in this __init__ method
        '''
        self.config_info=read_yaml_file(file_path=config_file_path) # readnig YAML file and assigning to object variable config_info
                                                                    # reading YAML file calling all get menthod define in this 
                                                                    # function to get configuration entatied
        
        

        self.training_pipeline_config=self.get_training_pipeline_config() ## In return value will be TrainingPipelineConfig (entity/namedtuple)
        
        self.time_stamp=current_time_stamp

        self.data_ingestion_config=self.get_data_ingestion_config()

        self.data_validation_config=self.get_data_validation_config()

        self.data_transformation_config=self.get_data_transformation_config()

        self.model_trainer_config=self.get_model_trainer_config()

        self.model_evaluation_config=self.get_model_evaluation_config()

        self.model_pusher_config=self.get_model_pusher_config()
    


    def get_training_pipeline_config(self) -> TrainingPipelineConfig:
        '''
        Info:
        Read Specific values from YAML file with the help of keys defined in CONSTANT module
        TrainingPipelineConfig = namedtuple("TrainingPipelineConfig", ["artifact_dir"]) --> Defined in entity > config_entity.py
        Need to assign one argument for "artifact_dir" to create TrainingPipelineConfig entity/namedTuple
        '''
        try:
            training_pipeline_info=self.config_info[TRAINING_PIPELINE_CONFIG_KEY]
            artifact_dir=os.path.join(ROOT_DIR,     
                                      training_pipeline_info[TRAINING_PIPELINE_NAME_KEY],
                                      training_pipeline_info[TRAINING_PIPELINE_ARTIFACT_DIR_KEY])
            training_pipeline_info=TrainingPipelineConfig(artifact_dir=artifact_dir) ## using TrainingPipelineConfig defined in entity > config_entity.py
            logging.info(f"Training Pipeline Configuration created as : {training_pipeline_info}")
            return training_pipeline_info

        except Exception as e:
            raise CustomeException(e,sys) from e
            

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        '''
        Info:
        Read Specific values from YAML file with the help of keys defined in CONSTANT module
        DataIngestionConfig=namedtuple("DataIngestionConfig",["dataset_download_url","download_dir","raw_data_dir",
                                        "ingested_train_dir","ingested_test_dir"])
        Need to assign "dataset_download_url","download_dir","raw_data_dir","ingested_train_dir","ingested_test_dir" 
        to create TrainingPipelineConfig entity/namedTuple
        '''
        try:
            artifact_dir=self.training_pipeline_config.artifact_dir
            data_ingestion_artifact_dir=os.path.join(artifact_dir,
                                                    DATA_INGESTION_ARTIFACT_DIR,
                                                    self.time_stamp)                                     
            # getting artifact directory created in get_training_pipeline_config() method
            # combining it with data_ingestion_artifact_dir and time_stamp
            
            data_ingestion_info=self.config_info[DATA_INGESTION_CONFIG_KEY]
            
            dataset_source_url=data_ingestion_info[DATA_INGESTION_DOWNLOAD_URL_KEY]

            # sample folder structure : concret\\artifact\\data_ingestion\\2022-07-09-23-12-32\\downloaded_data
            #                           concret\\artifact\\data_ingestion\\2022-07-09-23-12-32\\raw_data
            #                           concret\\artifact\\data_ingestion\\2022-07-09-23-12-32\\ingested_data\\train
            #                           concret\\artifact\\data_ingestion\\2022-07-09-23-12-32\\ingested_data\\test

            # Crating folder path for DATA download
            download_dir=os.path.join(data_ingestion_artifact_dir,
                                     data_ingestion_info[DATA_INGESTION_DOWNLOAD_DIR_KEY])
            
            # Crating folder path for raw data
            raw_data_dir=os.path.join(data_ingestion_artifact_dir,
                                      data_ingestion_info[DATA_INGESTION_RAW_DATA_DIR_KEY])
            
            # Crating folder path for ingested data --> Ingested data folder will have two sub-folder Train Data , Test Data
            ingested_data_dir = os.path.join(data_ingestion_artifact_dir,
                                            data_ingestion_info[DATA_INGESTION_INGESTED_DIR_NAME_KEY])

            # Crating folder path for train data
            ingested_train_dir=os.path.join(ingested_data_dir,
                                            data_ingestion_info[DATA_INGESTION_TRAIN_DIR_KEY])

            # Crating folder path for test data
            ingested_test_dir=os.path.join(ingested_data_dir,
                                            data_ingestion_info[DATA_INGESTION_TEST_DIR_KEY])
            
            ## using DataIngestionConfig defined in entity > config_entity.py
            data_ingestion_info=DataIngestionConfig(dataset_source_url=dataset_source_url,
                                                     download_dir=download_dir,
                                                     raw_data_dir=raw_data_dir,
                                                     ingested_train_dir=ingested_train_dir,
                                                     ingested_test_dir=ingested_test_dir)

            logging.info(f"Data Ingestion Configuration created as : {data_ingestion_info}")
            return data_ingestion_info

        except Exception as e:
            raise CustomeException(e,sys)  from e
 


    def get_data_validation_config(self) -> DataValidationConfig:
        '''
        Info:

        '''
        try:
            artifact_dir=self.training_pipeline_config.artifact_dir
            data_validation_artifact_dir=os.path.join(artifact_dir,
                                                    DATA_VALIDATION_ARTIFACT_DIR_NAME,
                                                    self.time_stamp)                                     
            # getting artifact directory created in get_training_pipeline_config() method
            # combining it with data_validation_artifact_dir and time_stamp

            data_validation_config=self.config_info[DATA_VALIDATION_CONFIG_KEY]
            
            schema_file_path=os.path.join(ROOT_DIR, 
                                          data_validation_config[DATA_VALIDATION_SCHEMA_DIR_KEY],
                                          data_validation_config[DATA_VALIDATION_SCHEMA_FILE_NAME_KEY])
            
            report_file_path = os.path.join(data_validation_artifact_dir,
                                            data_validation_config[DATA_VALIDATION_REPORT_FILE_NAME_KEY])

            report_page_file_path = os.path.join(data_validation_artifact_dir,
                                                data_validation_config[DATA_VALIDATION_REPORT_PAGE_FILE_NAME_KEY])

            ## using DataValidationConfig defined in entity > config_entity.py                             
            data_validation_config=DataValidationConfig(schema_file_path=schema_file_path,
                                                        report_file_path=report_file_path,
                                                        report_page_file_path=report_page_file_path)
            
            logging.info(f"Data Validation Configuration created as : {data_validation_config}")
            return data_validation_config 
        except Exception as e:
            raise CustomeException(e,sys) from e



    def get_data_transformation_config(self) -> DataTransformationConfig:
        '''
        Info:
        Use for Data preprocessing and Transformation Configuration
        Creating and returning DataTransformationConfig
        '''
        try:
            artifact_dir = self.training_pipeline_config.artifact_dir

            data_transformation_artifact_dir=os.path.join(
                artifact_dir,
                DATA_TRANSFORMATION_ARTIFACT_DIR,
                self.time_stamp)

            data_transformation_config_info=self.config_info[DATA_TRANSFORMATION_CONFIG_KEY]

            add_total_aggregate=data_transformation_config_info[DATA_TRANSFORMATION_ADD_NEW_COL_KEY]


            preprocessed_object_file_path = os.path.join(data_transformation_artifact_dir,
                                                        data_transformation_config_info[DATA_TRANSFORMATION_PREPROCESSING_DIR_KEY],
                                                        data_transformation_config_info[DATA_TRANSFORMATION_PREPROCESSED_FILE_NAME_KEY])

            
            transformed_train_dir=os.path.join(data_transformation_artifact_dir,
                                               data_transformation_config_info[DATA_TRANSFORMATION_DIR_NAME_KEY],
                                               data_transformation_config_info[DATA_TRANSFORMATION_TRAIN_DIR_NAME_KEY])


            transformed_test_dir = os.path.join(data_transformation_artifact_dir,
                                                data_transformation_config_info[DATA_TRANSFORMATION_DIR_NAME_KEY],
                                                data_transformation_config_info[DATA_TRANSFORMATION_TEST_DIR_NAME_KEY])
            

            data_transformation_config=DataTransformationConfig(add_total_aggregate=add_total_aggregate,
                                                                preprocessed_object_file_path=preprocessed_object_file_path,
                                                                transformed_train_dir=transformed_train_dir,
                                                                transformed_test_dir=transformed_test_dir)

            logging.info(f"Data transformation config: {data_transformation_config}")
            
            return data_transformation_config
        except Exception as e:
            raise CustomeException(e,sys) from e



    def get_model_trainer_config(self) -> ModelTrainerConfig:
        '''
        Info:

        '''
        try:
            pass
        except Exception as e:
            raise CustomeException(e,sys) from e



    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        '''
        Info:

        '''
        try:
            pass
        except Exception as e:
            raise CustomeException(e,sys) from e



    def get_model_pusher_config(self) -> ModelPusherConfig:
        '''
        Info:

        '''
        try:
            pass
        except Exception as e:
            raise CustomeException(e,sys) from e