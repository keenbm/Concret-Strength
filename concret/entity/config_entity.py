from collections import namedtuple


# For defining Named tuple skeleton for configuration related operation
# In Code now we can use object for namedtuple a=DataIngestionConfig("dataset_source_url","tgz_download_dir","raw_data_dir","ingested_train_dir","ingested_test_dir")
# This tyep of assigned basically creats structure for different different operation

DataIngestionConfig=namedtuple("DataIngestionConfig",
["dataset_source_url","download_dir","raw_data_dir","ingested_train_dir","ingested_test_dir"])


DataValidationConfig = namedtuple("DataValidationConfig", ["schema_file_path","report_file_path","report_page_file_path"])

DataTransformationConfig = namedtuple("DataTransformationConfig", ["add_new_col",
                                                                   "transformed_train_dir",
                                                                   "transformed_test_dir",
                                                                   "preprocessed_object_file_path"])


ModelTrainerConfig = namedtuple("ModelTrainerConfig", ["trained_model_file_path","base_accuracy","model_config_file_path"])

ModelEvaluationConfig = namedtuple("ModelEvaluationConfig", ["model_evaluation_file_path","time_stamp"])


ModelPusherConfig = namedtuple("ModelPusherConfig", ["export_dir_path"])

TrainingPipelineConfig = namedtuple("TrainingPipelineConfig", ["artifact_dir"])

