from concret.entity.config_entity import DataIngestionConfig
from concret.entity.artifact_entity import DataIngestionArtifact

## Importing constans from constant module
from concret.constant import *

from concret.exception import CustomException
from concret.logger import logging
import sys
import os

import tarfile
from six.moves import urllib

import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import train_test_split


class DataIngestion:
    '''
    Info:
    DataIngestion class is having Methods/Functions for creating data ingestion realted artifacts
    '''    

    def __init__(self,data_ingestion_config:DataIngestionConfig):
        '''
        When DataIngestion() class object is created , it'll get all configuration data from Configuration() class and
        and create data ingestion related artifact
        - All the class methods are initiated/clled in this __init__ method
        '''
        try:
            logging.info(f"{'='*20} Data Ingestion log started.{'='*20}")
            self.data_ingestion_config=data_ingestion_config
            #logging.info(f"Printing data_ingestion_config : {data_ingestion_config()}")

        except Exception as e:
            raise CustomException(e,sys) from e


    def download_data(self,) -> str:
        try:
            # Extrating remote url to download dataset
            download_url=self.data_ingestion_config.dataset_source_url
            downloaded_file_name=os.path.basename(download_url) # get downloaded file name

            #folder location for download datasetd
            download_dir=self.data_ingestion_config.download_dir

            # Delete old folder if it already exists
            if os.path.exists(download_dir):
                os.remove(download_dir)

            os.makedirs(download_dir,exist_ok=True) # If directory exists not present create new

            # Create complete file path (folder+filename)
            downloaded_file_path=os.path.join(download_dir,downloaded_file_name)

            # Downloading file in download_dir
            logging.info(f"Downloading data from {download_url} and storing it in {downloaded_file_path}")
            urllib.request.urlretrieve(download_url,downloaded_file_path)
            logging.info(f"Data Successfully Downloaded from {download_url} and stored in {downloaded_file_path}")
            return downloaded_file_path

        except Exception as e:
            raise CustomException(e,sys) from e        


    def extract_downloaded_data(self,downloaded_file_path):
        try:
            raw_data_dir=self.data_ingestion_config.raw_data_dir
            
            # Delete old folder if it already exists
            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)
            os.makedirs(raw_data_dir,exist_ok=True) # If directory exists not present create new

            # Converting data into panda dataframe and saving it as a CSV
            if os.path.splitext(downloaded_file_path)[-1].lower()[:4]==".xls":
                raw_data_frame=pd.read_excel(downloaded_file_path)
            else:
                raw_data_frame=pd.read_csv(downloaded_file_path)

            raw_data_dir_file=os.path.join(raw_data_dir,"raw_data.csv")
            
            # removing trailing and leading space in Column name before saving it
            raw_data_frame.columns=raw_data_frame.columns.str.strip()
            raw_data_frame.to_csv(raw_data_dir_file,index = False)

            #os.popen('copy downloaded_file_path raw_data_dir') # Copying downloaded file to raw data folder           
            logging.info(f"Successfully converted downloaed file to CSV and Saved at {raw_data_dir_file}")

            # This function can be modified used for extracting data if downloaded data is in zip ,tar format

        except Exception as e:
            raise CustomException(e,sys) from e  


    def split_data_as_train_test(self,)->DataIngestionArtifact:
        try:
            raw_data_dir=self.data_ingestion_config.raw_data_dir


            file_name = os.listdir(raw_data_dir)[0] # Getting file name from folder

            raw_data_file_path=os.path.join(raw_data_dir,file_name) # Combine file name

            # Converting data into panda dataframe
            raw_data_frame=pd.read_csv(raw_data_file_path)

            train_set = None
            test_set = None

            ## For this project using direct Train , Test Split
            train_set, test_set= train_test_split(raw_data_frame,random_state=42, train_size = .80)

            ## Creating TRAIN file path and storing csv
            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,"train_data.csv")
            if train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                train_set.to_csv(train_file_path,index=False)


            ## Creating Test file path and storing csv
            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,"test_data.csv")
            if test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir,exist_ok=True)
                test_set.to_csv(test_file_path,index=False)
            

            data_ingestion_artifact=DataIngestionArtifact(train_file_path=train_file_path,
                                                         test_file_path=test_file_path,
                                                         is_ingested=True,
                                                         message=f"Data Ingestion Completed successfully")

            logging.info(f"Train Test Split created successfully")
            
            return data_ingestion_artifact
        except Exception as e:
            raise CustomException(e,sys) from e  

    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        '''
        Info: 
        Calling all data methods of class in this method
        download_data , extract_downloaded_data , split_data_as_train_test and creating dataingestion artifact
        '''
        try:
            downloaded_file_path=self.download_data()
            raw_data_dir=self.extract_downloaded_data(downloaded_file_path)
            data_ingestion_artifact=self.split_data_as_train_test()
            logging.info("Data Ingestion artifact created : {data_ingestion_artifact}")

            return data_ingestion_artifact

        except Exception as e:
            raise CustomException(e,sys) from e

    # This method executed when this class is destroyed
    def __del__(self):
        logging.info(f"{'='*20} Data Ingestion log Completed.{'='*20}")

