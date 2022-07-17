# Concret-Strength

1. Setup Virtual Environment
   ```bash
   conda create -p concret-venv python==3.7 -y
   #-p : create environemnt in current directory
   conda activate concret-venv/  # Activate virtual environment
   ```

2. Creating Project structure
   ```bash
   CONCRET-STRENGTH
   ├── config
   |   ├──config.yaml --> Essential Values For configuration 
   |   ├──model.yaml --> Essential Values for model training and evaluation
   │   └──schema.yaml --> Essential Values for DataSet Schema
   ├── concret
   |   ├──component
   |   |  ├──_init_.py
   |   |  ├──data_eda.py
   |   |  ├──data_ingestion.py
   |   |  ├──data_transformation.py
   |   |  ├──data_validation.py
   |   |  ├──model_evaluation.py
   |   |  ├──model_pusher.py
   |   |  └──model_trainer.py
   |   ├──config
   |   |  ├──_init_.py
   |   |  └──configuration.py --> Class and methods coded to get confuguration data (returns configuration data(entity) having format defined in entity)
   |   ├──constant
   |   |  └──_init_.py
   |   ├──entity
   |   |  ├──_init_.py
   |   |  ├──artifact_entity.py --> For defining Named tuple skeleton for artifact related operation
   |   |  └──config_entity.py --> For defining Named tuple skeleton for configuration related operation
   |   ├──exception
   |   |  └──_init_.py
   |   ├──logger
   |   |  └──_init_.py
   |   ├──pipeline
   |   |  ├──_init_.py
   |   |  └──pipeline.py
   │   └──util
   |   |  ├──_init_.py
   |   |  └──util.py
   |   └──_init_.py
   ├── .github
   |   └──workflows
   |      └──main.yaml --> YAML file for Heroku/Amazon deployment using GitHub Action
   |── notebooks
   |── app.py
   |── trial.py
   |── requirement.txt
   |── setup.py
   |── Dockerfile --> File for creating docker image
   |── .dockerignore --> Ignore file while creating Docker Image
   └── README.md
   ```

3. coding requirement.txt and setup.py

4. coding Custome exception and logger
   concret>exception>__init__.py
   concret>logger>__init__.py

5. coding concret>constant>__init__.py

6. coding config>config.yaml , schema.yaml , model.yaml

7. coding concret>entity artifact_entity.py , config_entity.py

8. coding concret>util>util.py for supporting functions

9. coding concret>config>configuration.py --> In this file Configuraiton() class is created. In Configuraiton() class diff. diff get method created to fetch/get diff. diff. task configuation.
   - i.e. get_training_pipeline_config , get_data_ingestion_config , data_validation_config etc etc...
   - all get_ methods are called in __init__ method of the class.
   - So once Configuraiton() class object is created , all type of configuration data can be fetched from that class object
   - Code in oncret>config>configuration.py creats only configuration (tuple with file path and any other details)

10. coding python file under component folder once code for specific task is completed in configuration.py
      - i.e. once get_data_ingestion() methos is ready in configuration.py>Configuration class , start coding component>data_ingestion.py
      - Files in this folder created artifacts (actual data download and storage,tranin data , test data ,model creation and storage etc..) as per the configuration received from configuration.py

11. Coding Pipeline>pipeline.py
      - In this code we crated pipeline() class
      - pipeline() class consists of method slike start_data_ingestion,start_data_validation , start_model_trainer etc etc...
      - Configuration() class object to be passed in pipeline class internal methods
      - Also, data_ingestion(),data_validation() etc etc. classe object to be passed in pipeline class internal methods
      - So, this file basically collect configuration and perform ML lifecycle task sequentialy

12. Entity > model_factory.py
    '''
    from concret.entity.model_factory import ModelFactory,get_sample_model_config_yaml_file
    get_sample_model_config_yaml_file(export_dir="config")
    '''

    nodel_factory.py -> For preparig Model.
    When below code executed , it creates YAML template for model confuguration
    
    ```bash
    get_sample_model_config_yaml_file(export_dir="config")
    ```
    
    ![This is an image] (/readme Imgs/Model Config YAML-1.PNG)
    
    After modifying model factory YAML file (refer below image):
    This YAML file an be used for model training_pipeline_info



## Pending Items :
- data_validation --> Checking details to be coded
- data_validation --> Previous dataset Vs. Current dataset data drift checking code to be added
