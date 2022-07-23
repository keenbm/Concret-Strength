from concret.logger import logging
from concret.exception import CustomException
from concret.entity.config_entity import ModelEvaluationConfig
from concret.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,ModelTrainerArtifact,ModelEvaluationArtifact
from concret.constant import *
import numpy as np
import os
import sys
from concret.util.util import write_yaml_file, read_yaml_file, load_object,load_data
from concret.entity.model_factory import evaluate_regression_model




class ModelEvaluation:

    def __init__(self, model_evaluation_config: ModelEvaluationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            logging.info(f"{'>>' * 30}Model Evaluation log started.{'<<' * 30} ")
            self.model_evaluation_config = model_evaluation_config
            self.model_trainer_artifact = model_trainer_artifact
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_best_model(self):
        try:
            
            model = None
            model_evaluation_file_path = self.model_evaluation_config.model_evaluation_file_path

            # If Model detal not available in concret\artifact\model_evaluation\model_evaluation.yaml file 
            # thn, this If condition will be executed
            # i.e. running pipe line for the first time
            if not os.path.exists(model_evaluation_file_path):
                write_yaml_file(file_path=model_evaluation_file_path,
                                )
                return model
            model_eval_file_content = read_yaml_file(file_path=model_evaluation_file_path)


            # if  model_evaluation.yaml is None , return empty dictonary
            # if not None , return model_evaluation.yaml file content
            model_eval_file_content = dict() if model_eval_file_content is None else model_eval_file_content

            # Checking if BEST_MODEL_KEY is available in 
            # concret\artifact\model_evaluation\model_evaluation.yaml
            # If note available returnin  Model = None
            if BEST_MODEL_KEY not in model_eval_file_content:
                return model

            # If concret\artifact\model_evaluation\model_evaluation.yaml available and
            # BEST_MODEL_KEY is present then , returning BEST_MODEl path mentioned in above YAML file
            model = load_object(file_path=model_eval_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY])
            return model
        except Exception as e:
            raise CustomException(e, sys) from e

    def update_evaluation_report(self, model_evaluation_artifact: ModelEvaluationArtifact):
        '''
        If current trained model is better thn already existing model
        (mentioned in concret\artifact\model_evaluation\model_evaluation.yaml)
        thn, this function update concret\artifact\model_evaluation\model_evaluation.yaml file
        '''
        try:
            eval_file_path = self.model_evaluation_config.model_evaluation_file_path
            model_eval_content = read_yaml_file(file_path=eval_file_path)
            
            # if  model_evaluation.yaml is None , return empty dictonary
            # if not None , return model_evaluation.yaml file content
            model_eval_content = dict() if model_eval_content is None else model_eval_content
            
            
            previous_best_model = None

            if BEST_MODEL_KEY in model_eval_content:
                previous_best_model = model_eval_content[BEST_MODEL_KEY]

            logging.info(f"Previous eval result: {model_eval_content}")

            # Creating KEY and Value dictonary for Newly Trained model
            # Similer format to model_evaluation.yaml
            eval_result = {
                BEST_MODEL_KEY: {
                    MODEL_PATH_KEY: model_evaluation_artifact.evaluated_model_path,
                }
            }

            # If there is existing model detail in model_evaluation.yaml
            # Create History log for old/previous best model
            if previous_best_model is not None:
                model_history = {self.model_evaluation_config.time_stamp: previous_best_model}
                if HISTORY_KEY not in model_eval_content:
                    history = {HISTORY_KEY: model_history}
                    eval_result.update(history)
                else:
                    model_eval_content[HISTORY_KEY].update(model_history)

            # Update model_evaluation.yaml
            model_eval_content.update(eval_result)
            logging.info(f"Updated eval result:{model_eval_content}")
            write_yaml_file(file_path=eval_file_path, data=model_eval_content)

        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        '''
        Creats artifact\model_evaluation\model_evaluation.yaml 
        In model_evaluation.yaml  --> Store Best Model
        '''
        try:
            trained_model_file_path = self.model_trainer_artifact.trained_model_file_path
            trained_model_object = load_object(file_path=trained_model_file_path)

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            schema_file_path = self.data_validation_artifact.schema_file_path

            train_dataframe = load_data(file_path=train_file_path,
                                                           schema_file_path=schema_file_path,
                                                           )
            test_dataframe = load_data(file_path=test_file_path,
                                                          schema_file_path=schema_file_path,
                                                          )
            schema_content = read_yaml_file(file_path=schema_file_path)
            target_column_name = schema_content[TARGET_COLUMN_KEY]

            # target_column
            logging.info(f"Converting target column into numpy array.")
            train_target_arr = np.array(train_dataframe[target_column_name])
            test_target_arr = np.array(test_dataframe[target_column_name])
            logging.info(f"Conversion completed target column into numpy array.")

            # dropping target column from the dataframe
            logging.info(f"Dropping target column from the dataframe.")
            train_dataframe.drop(target_column_name, axis=1, inplace=True)
            test_dataframe.drop(target_column_name, axis=1, inplace=True)
            logging.info(f"Dropping target column from the dataframe completed.")

            # Getting previous best model
            model = self.get_best_model()

            # If there is no previous best(Production) model then accept current model as best model
            # Also store current model as best model and update/create
            # artifact\model_evaluation\model_evaluation.yaml
            if model is None:
                logging.info("Not found any existing model. Hence accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
                return model_evaluation_artifact

            # If there is model stored in artifact\model_evaluation\model_evaluation.yaml as best model
            # Load that model
            # Compare previous best Model and Current Model
            model_list = [model, trained_model_object]

            # Passing previous best model = model & current model = trained_model_object
            # to evaluate_regression_model function mentioned in model_factory
            # This function gives best model out of all passed model (Previous Best Vs. Current Best)
            # Also this function check Base aaccuracy
            metric_info_artifact = evaluate_regression_model(model_list=model_list,
                                                               X_train=train_dataframe,
                                                               y_train=train_target_arr,
                                                               X_test=test_dataframe,
                                                               y_test=test_target_arr,
                                                               base_accuracy=self.model_trainer_artifact.model_accuracy,
                                                               )
            
            logging.info(f"Model evaluation completed. model metric artifact: {metric_info_artifact}")

            # If evaluate_regression_model->metric_info_artifact=None , return NONE that means
            # Both previous as well as current model does not fullfill BASE ACCURACY thresold defined in config file
            # create response stating is_model_accepted=False and return the same
            if metric_info_artifact is None:
                response = ModelEvaluationArtifact(is_model_accepted=False,
                                                   evaluated_model_path=trained_model_file_path
                                                   )
                logging.info(response)
                return response

            # # If evaluate_regression_model->metric_info_artifact=1 , return 1 taht means
            # Current trained model is having better accuracy
            # So, consider Current model as a best model /production
            # Also update artifact\model_evaluation\model_evaluation.yaml
            if metric_info_artifact.index_number == 1:
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
            else:
                logging.info("Trained model is no better than existing model hence not accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=False)
            return model_evaluation_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def __del__(self):
        logging.info(f"{'=' * 20}Model Evaluation log completed.{'=' * 20} ")