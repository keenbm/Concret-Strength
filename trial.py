from concret.pipeline.pipeline import Pipeline
from concret.exception import CustomException
from concret.logger import logging
import sys

def main():
    try:
        pipeline=Pipeline()
        pipeline.run_pipeline()
    except Exception as e:
        print(e)
        raise CustomException(e,sys) from e
            

if __name__=="__main__":
    main()