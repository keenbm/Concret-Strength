from concret.entity.config_entity import DataIngestionConfig
from concret.entity.artifact_entity import DataIngestionArtifict

## Importing constans from constant module
from concret.constant import *

from concret.exception import CustomeException
from concret.logger import logging
import sys

import tarfile
from six.moves import urllib

import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit


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
        except Exception as e:
            raise CustomeException(e,sys) from e


    def download_data(self,) -> str:
        try:
            # Extrating remote url to download dataset
            download_url=self.data_ingestion_config.dataset_download_url
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
            urllib.request(download_url,downloaded_file_path)
            logging.info(f"Data Successfully Downloaded from {download_url} and stored in {downloaded_file_path}")
            return downloaded_file_path

        except Exception as e:
            raise CustomeException(e,sys) from e        



    def extract_downloaded_data(self,downloaded_file_path):
        try:
            raw_data_dir=self.data_ingestion_config.raw_data_dir
            
            # Delete old folder if it already exists
            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)
            os.makedirs(raw_data_dir,exist_ok=True) # If directory exists not present create new


            logging.info(f"Copying downloaded file {downloaded_file_path} to {raw_data_dir}")
            os.popen('copy downloaded_file_path raw_data_dir') # Copying downloaded file to raw data folder           
            logging.info(f"Successfully Copied {downloaded_file_path} to {raw_data_dir}")

            # This function can be modified used for extracting data if downloaded data is in zip ,tar format

        except Exception as e:
            raise CustomeException(e,sys) from e  



    def split_data_as_train_test(self,)->DataIngestionArtifict:
        try:
            raw_data_dir=self.data_ingestion_config.raw_data_dir

            file_name=os.listdir(raw_data_dir)[0] # Getting file name from folder

            raw_data_file_path=os.path.join(raw_data_dir,file_name) # Combine file name

            # Converting data into panda dataframe
            if os.path.splitext(raw_data_file_path)[-1].lower()[:4]==".xls":
                raw_data_frame=pd.read_excel(raw_data_file_path) 
            else:
                raw_data_frame=pd.read_csv(raw_data_file_path)


            logging.info(f"Data Downloaded from {1}")
        except Exception as e:
            raise CustomeException(e,sys) from e  

    def initiate_data_ingestion(self)-> DataIngestionArtifict:
        '''
        Info: 
        Calling all data methods of class in this method
        download_data , extract_downloaded_data , split_data_as_train_test
        '''
        try:
            downloaded_file_path=self.download_data()
            raw_data_dir=self.extract_downloaded_data(downloaded_file_path)

        except Exception as e:
            raise CustomeException(e,sys) from e


