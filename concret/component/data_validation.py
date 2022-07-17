from concret.entity.config_entity import DataValidationConfig
from concret.entity.artifact_entity import DataValidationArtifact

## Importing constans from constant module
from concret.constant import *
from concret.util.util import read_yaml_file

from concret.exception import CustomException
from concret.logger import logging
import sys
import os
import pandas as pd

# evidently library for checkig datadrift and creating report
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab
import json


class DataValidation:
    '''
    Info:
    DataIngestion class is having Methods/Functions for creating data validation realted artifacts
    '''  

    def __init__(self,data_validation_config:DataValidationConfig,
                data_ingestion_artifact:DataValidationArtifact):
        try:
            logging.info(f"{'>>'*30}Data Valdaition log started.{'<<'*30} \n\n")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise CustomException(e,sys) from e
    

    def get_train_and_test_df(self):
        try:
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df,test_df
        except Exception as e:
            raise CustomException(e,sys) from e

    def is_train_test_file_exists(self)->bool:
        '''
        Info:
        Checks if train and Test file exists or not and pass it to 
        '''
        try:
            logging.info("Checking if training and test file is available")
            is_train_file_exists=False
            is_test_file_exists=False

            train_file_path=self.data_ingestion_artifact.train_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            is_train_file_exists=os.path.exists(train_file_path)
            is_test_file_exists=os.path.exists(test_file_path)
            is_available=is_train_file_exists and is_test_file_exists

            logging.info(f"Is train and test file exists ? - {is_available}")

            return is_available

        except Exception as e:
            raise CustomException(e,sys) from e

    def validate_dataset_schema(self)->bool:
        '''
        Info:
        Checks Dataset is as per Schema
        Also Change Column names as per schema
        '''
        try:
            
            schema_validation_status = False
            schema_file_path = self.data_validation_config.schema_file_path
            dataset_schema = read_yaml_file(file_path=schema_file_path)
            original_col_name=list(dataset_schema[DATA_VALIDATION_COL_NAME_MAP_KEY].keys())
            new_col_name=list(dataset_schema[DATA_VALIDATION_COL_NAME_MAP_KEY].values())

            ## 1. Checking columns Names
            train_df,test_df = self.get_train_and_test_df()
            
            if (list(train_df.columns) == list(test_df.columns) == original_col_name):
                train_df.columns=new_col_name
                train_df.to_csv(self.data_ingestion_artifact.train_file_path,index = False)
                
                test_df.columns=new_col_name
                test_df.to_csv(self.data_ingestion_artifact.test_file_path,index = False)

                schema_validation_status = True
                logging.info("schema column name validation SUCCESSFUL")

            else:
                schema_validation_status = False
                logging.warning("Downloaded data column names do not match with schema")
                raise Exception("Downloaded data column names do not match with schema")

            # Assigment validate training and testing dataset using schema file
            #1. Number of Column
            #2. Change column Names as per schema file
            #3. Check Categories for categorical columns 

            ## Will be implemented later
            
            return schema_validation_status 

        except Exception as e:
            raise CustomException(e,sys) from e

    def get_and_save_data_drift_report(self):
        '''
        Info: Creats Data Drift report in JSON format
        Using Evidently Library checking data drift in dataset between Training and Testing data Set
        Also checks previous data set with current data set
        '''
        try:
        
            profile = Profile(sections=[DataDriftProfileSection()]) #From Evidently library

            train_df,test_df = self.get_train_and_test_df()

            profile.calculate(train_df,test_df) #Using Evidently library creating data drift profile for train_df and test_df

            # To Be implemented in future -> Also implement Previous data Vs current data profile to check data dift

            report = json.loads(profile.json())

            report_file_path = self.data_validation_config.report_file_path
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir,exist_ok=True)

            with open(report_file_path,"w") as report_file:
                json.dump(report, report_file, indent=6)
            return report
        except Exception as e:
            raise CustomException(e,sys) from e

    def save_data_drift_report_page(self):
        '''
        Info :
        Creats HTML page - Graph using for Data Drift Check
        '''
        try:
            dashboard = Dashboard(tabs=[DataDriftTab()]) ## From Evidently Library
            train_df,test_df = self.get_train_and_test_df()
            dashboard.calculate(train_df,test_df)

            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = os.path.dirname(report_page_file_path)
            os.makedirs(report_page_dir,exist_ok=True)

            dashboard.save(report_page_file_path)
        except Exception as e:
            raise CustomException(e,sys) from e

    def is_data_drift_found(self)->bool:
        '''
        Info:
        Create Data Drift report and Data Drift page
        using above two methods
        '''
        try:
            report = self.get_and_save_data_drift_report()
            self.save_data_drift_report_page()

            ## To be implemented --> Actual result for the is_data_drift_found to be fetched from JSON report and retured
            return True
        except Exception as e:
            raise CustomException(e,sys) from e


    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            is_available=self.is_train_test_file_exists()
            schema_validation_status=self.validate_dataset_schema()
            self.is_data_drift_found()

            data_validation_artifact = DataValidationArtifact(schema_file_path=self.data_validation_config.schema_file_path,
                                                             report_file_path=self.data_validation_config.report_file_path,
                                                             report_page_file_path=self.data_validation_config.report_page_file_path,
                                                             is_validated=True,
                                                             message="Data Validation performed successully.")

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise CustomException(e,sys) from e
    

    def __del__(self):
        logging.info(f"{'>>'*30}Data Valdaition log completed.{'<<'*30} \n\n")
