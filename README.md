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
   |   ├──config.yaml
   |   ├──model.yaml
   │   └──schema.yaml
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
   |   |  └──configuration.py
   |   ├──constant
   |   |  └──_init_.py
   |   ├──entity
   |   |  ├──_init_.py
   |   |  ├──artifact_entity.py
   |   |  └──config_entity.py
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
   |── notebook
   |── app.py
   |── trial.py
   |── requirement.txt
   |── setup.py
   |── Dockerfile
   └── README.md
   ```