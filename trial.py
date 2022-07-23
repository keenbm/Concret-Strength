from concret.pipeline.pipeline import Pipeline
from concret.exception import CustomException
from concret.logger import logging
from concret.config.configuration import Configuration
import os,sys

def main():
    try:
        config_file_path=os.path.join("config","config.yaml")
        pipeline=Pipeline(Configuration(config_file_path))
        pipeline.run_pipeline()
    except Exception as e:
        print(e)
        raise CustomException(e,sys) from e
            

if __name__=="__main__":
    main()