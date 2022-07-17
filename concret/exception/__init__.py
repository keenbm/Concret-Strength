import os 
import sys


## Creating Custome Exception Class
class CustomException(Exception):
    '''
    Description : This Calls if for custome exception
    Use : This class will gives exception message along with exact line number
    Object of this calss to be created when exception occures
    i.e.
    try:
        code
    except Exception as e:
            raise CustomException(e,sys) from e
    '''

    def __init__(self,error_message:Exception,error_detail:sys):

        super().__init__(error_message) ## Inhereting from python in-built Exception class
        self.error_message=CustomException.get_detailed_error_message(error_message=error_message,
                                                                       error_detail=error_detail)
    
   
    @staticmethod ## We can directly call this method without creating object
    def get_detailed_error_message(error_message:Exception,error_detail:sys)->str:
        # ->str : Means function return string type data
               
        """
        error_message: Exception object
        error_detail: object of sys module
        """
        _,_ ,exec_tb = error_detail.exc_info()
        exception_block_line_number = exec_tb.tb_frame.f_lineno
        try_block_line_number = exec_tb.tb_lineno
        file_name = exec_tb.tb_frame.f_code.co_filename
        error_message = f"""
        Error occured in script: 
        [ {file_name} ] at 
        try block line number: [{try_block_line_number}] and exception block line number: [{exception_block_line_number}] 
        error message: [{error_message}]
        """
        return error_message


    def __str__(self):
        '''
        To represents the class objects as a string 
        when object print(myObject.__str__())
        is gives output as CustomException(error_message:Exception,error_detail:sys)
        '''
        # If we dont use __str__ method output will be pointer of object : <__main__.CustomException object at 0x7f5cbb8eb1f0>
        return self.error_message


    def __repr__(self) -> str:
        '''
        This print object as pointer : <__main__.CustomException object at 0x7f5cbb8eb1f0>
        '''
        return CustomException.__name__.str()