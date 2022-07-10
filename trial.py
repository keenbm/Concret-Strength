from concret.pipeline.pipeline import Pipeline
from concret.exception import CustomeException
from concret.logger import logging
import sys

def main():
    try:
        pipeline=Pipeline()
        pipeline.run_pipeline()
    except Exception as e:
        print(e)
        raise CustomeException(e,sys) from e
            

if __name__=="__main__":
    main()