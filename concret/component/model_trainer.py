from concret.exception import CustomException
import os,sys
from concret.logger import logging
from typing import List
from concret.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from concret.entity.config_entity import ModelTrainerConfig
from concret.util.util import load_numpy_array_data,save_object,load_object
from concret.entity.model_factory import MetricInfoArtifact, ModelFactory,GridSearchedBestModel
from concret.entity.model_factory import evaluate_regression_model
from concret.constant import *
import mlflow
import mlflow.sklearn



class ConcretEstimatorModel:
    def __init__(self, preprocessing_object, trained_model_object):
        """
        TrainedModel constructor
        preprocessing_object: preprocessing_object
        trained_model_object: trained_model_object
        This class combined preprocessin object and Trained model object
        This Class object we are saving as final pickle file (model)
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object

    def predict(self, X):
        """
        function accepts raw inputs and then transformed raw input using preprocessing_object
        which gurantees that the inputs are in the same format as the training data
        At last it perform prediction on transformed features
        """
        transformed_feature = self.preprocessing_object.transform(X)
        return self.trained_model_object.predict(transformed_feature)

    def __repr__(self):
        return f"{type(self.trained_model_object).__name__}()"

    def __str__(self):
        return f"{type(self.trained_model_object).__name__}()"




class ModelTrainer:

    def __init__(self, model_trainer_config:ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            logging.info(f"{'>>' * 30}Model trainer log started.{'<<' * 30} ")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
                       
            #loading transformed training and testing datset
            logging.info(f"Loading transformed training dataset")
            transformed_train_file_path = self.data_transformation_artifact.transformed_train_file_path
            train_array = load_numpy_array_data(file_path=transformed_train_file_path)

            #reading model config file 
            #loading preprocessing object
            logging.info(f"Loading transformed testing dataset")
            transformed_test_file_path = self.data_transformation_artifact.transformed_test_file_path
            test_array = load_numpy_array_data(file_path=transformed_test_file_path)

            logging.info(f"Splitting training and testing input and target feature")
            x_train,y_train,x_test,y_test = train_array[:,:-1],train_array[:,-1],test_array[:,:-1],test_array[:,-1]
            

            logging.info(f"Extracting model config file path")
            model_config_file_path = self.model_trainer_config.model_config_file_path

            
            logging.info(f"Initializing model factory class using above model config file: {model_config_file_path}")
            model_factory = ModelFactory(model_config_path=model_config_file_path)
            
            
            base_accuracy = self.model_trainer_config.base_accuracy
            logging.info(f"Expected accuracy: {base_accuracy}")
            
            mlflow.set_experiment("Concret_Strength_Model")
            with mlflow.start_run():

                logging.info(f"Initiating operation model selecttion")
                # Getting best model based on  TRAINING DATA SET
                best_model = model_factory.get_best_model(X=x_train,y=y_train,base_accuracy=base_accuracy)
                
                
                logging.info(f"Best model found on training dataset: {best_model}")
                
                logging.info(f"Extracting trained model list.")
                grid_searched_best_model_list:List[GridSearchedBestModel]=model_factory.grid_searched_best_model_list
                mlflow.log_text(str(grid_searched_best_model_list), "Model/grid_searched_best_model_list.txt")
                
                model_list = [model.best_model for model in grid_searched_best_model_list ]
                logging.info(f"Evaluation all trained model on training and testing dataset both")
                #evaludation models on both training & testing datset -->model object
                # Here BEST MODEL is selected based on both Training and Testing accuracy.
                # Most generalized model will be selected
                metric_info:MetricInfoArtifact = evaluate_regression_model(model_list=model_list,X_train=x_train,y_train=y_train,X_test=x_test,y_test=y_test,base_accuracy=base_accuracy)
                mlflow.log_text(str(metric_info), "Model/metric_info.txt")
                logging.info(f"Best found model on both training and testing dataset.")
                
                preprocessing_obj=  load_object(file_path=self.data_transformation_artifact.preprocessed_object_file_path)
                model_object = metric_info.model_object

                trained_model_file_path=self.model_trainer_config.trained_model_file_path
                
                # Here both preprocessing pickle and best model pickel file combined
                # and saved as single combined pickel file
                # custom model object by combining both preprocessing obj and model obj
                concret_model = ConcretEstimatorModel(preprocessing_object=preprocessing_obj,trained_model_object=model_object)
                
                #saving combined model object in pickel format
                logging.info(f"Saving model at path: {trained_model_file_path}")
                save_object(file_path=trained_model_file_path,obj=concret_model)

                #saving Ml model without preprocessing_object
                #file_path_model_without_preprocessing=trained_model_file_path.replace("model.pkl","model_without_preprocessing.pkl")
                #save_object(file_path=file_path_model_without_preprocessing,obj=model_object)


                model_trainer_artifact=  ModelTrainerArtifact(is_trained=True,message="Model Trained successfully",
                trained_model_file_path=trained_model_file_path,
                train_rmse=metric_info.train_rmse,
                test_rmse=metric_info.test_rmse,
                train_accuracy=metric_info.train_accuracy,
                test_accuracy=metric_info.test_accuracy,
                model_accuracy=metric_info.model_accuracy
                )

                logging.info(f"Model Trainer Artifact: {model_trainer_artifact}")

                ## Logging Information using MLFlow
                                    
                # Logginh Parameter in ML Flow
                            
                for k,v in concret_model.trained_model_object.get_params().items():
                    mlflow.log_param(f"{k}",v)
                
                mlflow.log_metric("train_rmse",model_trainer_artifact.train_rmse)
                mlflow.log_metric("test_rmse",model_trainer_artifact.test_rmse)
                mlflow.log_metric("train_accuracy",model_trainer_artifact.train_accuracy)
                mlflow.log_metric("test_accuracy",model_trainer_artifact.test_accuracy)
                mlflow.log_metric("model_accuracy",model_trainer_artifact.model_accuracy)
                mlflow.log_artifact(model_trainer_artifact.trained_model_file_path,"Model")
                mlflow.log_text(f"Model Stored at : {model_trainer_artifact.trained_model_file_path}", "Model/model_okl_file_location.txt")
                mlflow.log_text(f"Transformation Pipeline data : {concret_model.preprocessing_object}", "Model/pre_processing_pipeline.txt")
                mlflow.log_text(f"ML Model Parameter : {concret_model.trained_model_object.get_params()}", "Model/ML_Model_Param.txt")
                #str()
                mlflow.end_run()
           
            return model_trainer_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def __del__(self):
        logging.info(f"{'>>' * 30}Model trainer log completed.{'<<' * 30} ")










