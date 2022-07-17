from cgi import test
from sklearn import preprocessing
from concret.exception import CustomException
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


class FeatureGenerator(BaseEstimator, TransformerMixin):
    '''
    This is custom class created for performing Feature Engineering
    Structure of this class is considered similer as sklearn library structure
    This Class to be used along with other Transformation function
    '''

    def __init__(self,
                add_total_aggregate=True,
                Coarse_Aggregate_ix=5,
                Fine_Aggregate_ix=6,
                columns=None):
        """
        FeatureGenerator Initialization
        add_total_aggregate: bool
        Coarse_Aggregate_ix: int index number of Coarse Aggregate
        Fine_Aggregate_ix: int index number of Fine Aggregate
        """
        try:
            self.columns = columns
            if self.columns is not None:
                Coarse_Aggregate_ix = self.columns.index(COLUMN_COARSE_AGGREGATE)
                Fine_Aggregate_ix = self.columns.index(COLUMN_FINE_AGGREGATE)

            self.add_total_aggregate = add_total_aggregate
            self.Coarse_Aggregate_ix = Coarse_Aggregate_ix
            self.Fine_Aggregate_ix = Fine_Aggregate_ix

        except Exception as e:
            raise CustomException(e, sys) from e


    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        try:
            ## Add Code related to feature engineering here
            ## For this porject only one additional column added 
            # Total_Aggregate = Coarse_Aggregate + Fine_Aggregate
            if self.add_total_aggregate:
                Total_Aggregate = X[:, self.Coarse_Aggregate_ix] + X[:, self.Fine_Aggregate_ix]
                generated_feature = np.c_[X, Total_Aggregate]
            else:
                generated_feature = np.c_[X]

            return generated_feature

        except Exception as e:
            raise CustomException(e, sys) from e




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
            raise CustomException(e,sys) from e
    
    

    def get_data_transformer_object(self)->ColumnTransformer:
        '''
        Creating Pipeline for Neumerical and Categorical columns to perform data Transformation fromusing
        Varioud SkLearn PIPELINE functions
        - NaN Value imputer
        - Feature engineering-->Custome Feature Generator
        - Standardization / Normalization
        '''
        try:
            schema_file_path = self.data_validation_artifact.schema_file_path

            dataset_schema = read_yaml_file(file_path=schema_file_path)

            numerical_columns = dataset_schema[NUMERICAL_COLUMN_KEY]
            
            # categorical_columns not applicable for this project
            #categorical_columns = dataset_schema[CATEGORICAL_COLUMN_KEY]


            # FeatureGenerator --> Custom Transformation class created above to create total_Aggregate column 
            num_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy="median")),
                ('feature_generator', FeatureGenerator(
                    add_total_aggregate=self.data_transformation_config.add_total_aggregate,
                    columns=numerical_columns)),
                ('scaler', StandardScaler())])
            
            logging.info(f"Numerical columns: {numerical_columns}")

            # Not applicable as there is no categorical in this project

            # cat_pipeline = Pipeline(steps=[
            #      ('impute', SimpleImputer(strategy="most_frequent")),
            #      ('one_hot_encoder', OneHotEncoder()),
            #      ('scaler', StandardScaler(with_mean=False))
            # ]
            # )


            # ColumnTransformer() from Sklearn can be used like below if there are multiple pipeline to be executed
            # i.e. Seperate pipeline for numerical data and Seperate pipeline for categorical data

            # preprocessing = ColumnTransformer([
            #     ('num_pipeline', num_pipeline, numerical_columns),
            #     ('cat_pipeline', cat_pipeline, categorical_columns),
            # ])

            
            # For this Project only Neumerical columns are available so ,...
            preprocessing = ColumnTransformer([
                ('num_pipeline', num_pipeline, numerical_columns)])

            return preprocessing

        except Exception as e:
            raise CustomException(e,sys) from e   
 

    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f"Obtaining preprocessing object.")
            
            ## Getting Preprocessing/Transformation Pipelien from above function
            preprocessing_obj = self.get_data_transformer_object()


            logging.info(f"Obtaining training and test file path.")
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            

            schema_file_path = self.data_validation_artifact.schema_file_path
            
            logging.info(f"Loading training and test data as pandas dataframe.")
            train_df = load_data(file_path=train_file_path, schema_file_path=schema_file_path)
            
            test_df = load_data(file_path=test_file_path, schema_file_path=schema_file_path)

            schema = read_yaml_file(file_path=schema_file_path)

            target_column_name = schema[TARGET_COLUMN_KEY]


            logging.info(f"Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df = test_df[target_column_name]
            

            # Applying Preprocession / Transformation pipeline on Data
            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            # Creating Test and Train np Array with --> Target Feature and Pre-processed / Transformed Input data for both TEST and TRAIN DATA
            train_arr = np.c_[ input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            
            # Getting directory location for storing pre-processed / Transformed data artifact
            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir

            # Creating file name for Transformed data 
            # Transformed data stored with .npz extention --> NumPy Array format
            train_file_name = os.path.basename(train_file_path).replace(".csv",".npz")
            test_file_name = os.path.basename(test_file_path).replace(".csv",".npz")

            # Creating complete path for Transformed data storage
            transformed_train_file_path = os.path.join(transformed_train_dir, train_file_name)
            transformed_test_file_path = os.path.join(transformed_test_dir, test_file_name)

            logging.info(f"Saving transformed training and testing array.")
            
            # Saving Transformed data (NumPy array format)
            save_numpy_array_data(file_path=transformed_train_file_path,array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path,array=test_arr)
            
            # Also Additionaly storing Tansformed Data in CSV for Testing
            new_col_name=list(schema[COLUMNS_NAME_AFTER_TRANSFORMATION_KEY])
            
            transfomed_train_df=pd.DataFrame(input_feature_train_arr)
            transfomed_train_df = pd.concat([transfomed_train_df, target_feature_train_df], axis=1)
            transfomed_train_df.columns=new_col_name
            transfomed_train_df.to_csv(transformed_train_file_path.replace(".npz",".csv"),index = False)
            
            transfomed_test_df=pd.DataFrame(input_feature_test_arr)
            transfomed_test_df = pd.concat([transfomed_test_df, target_feature_test_df], axis=1)
            transfomed_test_df.columns=new_col_name
            transfomed_test_df.to_csv(transformed_test_file_path.replace(".npz",".csv"),index = False)
            

            # Getting path for storing Transformation / Pre-processing pickle file
            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path
            logging.info(f"Saving preprocessing object.")
            
            # Saving Transformation / Pre-processing object pickle file
            # This to be used for future prediction
            save_object(file_path=preprocessing_obj_file_path,obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
            message="Data transformation successfull.",
            transformed_train_file_path=transformed_train_file_path,
            transformed_test_file_path=transformed_test_file_path,
            preprocessed_object_file_path=preprocessing_obj_file_path

            )
            logging.info(f"Data transformationa artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise CustomException(e,sys) from e

    def __del__(self):
        logging.info(f"{'>>'*30}Data Transformation log completed.{'<<'*30} \n\n")