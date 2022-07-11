from cgi import test
from sklearn import preprocessing
from concret.exception import CustomeException
from concret.logger import logging
from concret.constant import *
from concret.util.util import read_yaml_file,save_object,save_numpy_array_data,load_data
from concret.entity.config_entity import DataTransformationConfig 
from concret.entity.artifact_entity import DataIngestionArtifact,\
DataValidationArtifact,DataTransformationArtifact
import sys,os
import numpy as np
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import pandas as pd


class DataTransformation:

    def __init__(self, data_transformation_config: DataTransformationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact):
                 
        try:
            logging.info(f"{'>>' * 30}Data Transformation log started.{'<<' * 30} ")
            self.data_transformation_config= data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact

        except Exception as e:
            raise CustomeException(e,sys) from e