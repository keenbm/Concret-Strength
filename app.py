from flask import Flask
import sys
from concret.logger import logging
from concret.exception import CustomeException
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST']) # To render Homepage
def home_page():
    try:
        #raise Exception("We are testing custom exception")
        a=1/0
    except Exception as e:
        housing = CustomeException(e,sys)
        logging.info(housing.error_message)
        logging.info("We are testing logging module")
    return "CI CD pipeline has been established."

if __name__ == '__main__':
    app.run(debug=True)