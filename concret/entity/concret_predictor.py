import os
import sys

from concret.exception import CustomException
from concret.util.util import load_object

import pandas as pd


class ConcretData:

    def __init__(self,
                 Cement: float,
                 Furnace_Slag: float,
                 Fly_Ash: float,
                 Water: float,
                 Superplasticizer: float,
                 Coarse_Aggregate: float,
                 Fine_Aggregate: float,
                 Age: float,
                 Concrete_Compressive_Strength: float = None
                 ):
        try:
            self.Cement = Cement
            self.Furnace_Slag = Furnace_Slag
            self.Fly_Ash = Fly_Ash
            self.Water = Water
            self.Superplasticizer = Superplasticizer
            self.Coarse_Aggregate = Coarse_Aggregate
            self.Fine_Aggregate = Fine_Aggregate
            self.Age = Age
            self.Concrete_Compressive_Strength = Concrete_Compressive_Strength
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_concret_input_data_frame(self):

        try:
            concret_input_dict = self.get_concret_data_as_dict()
            return pd.DataFrame(concret_input_dict)
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_concret_data_as_dict(self):
        try:
            input_data = {
                "Cement": [self.Cement],
                "Furnace_Slag": [self.Furnace_Slag],
                "Fly_Ash": [self.Fly_Ash],
                "Water": [self.Water],
                "Superplasticizer": [self.Superplasticizer],
                "Coarse_Aggregate": [self.Coarse_Aggregate],
                "Fine_Aggregate": [self.Fine_Aggregate],
                "Age": [self.Age]}
            return input_data
        except Exception as e:
            raise CustomException(e, sys)


class ConcretPredictor:

    def __init__(self, model_dir: str):
        try:
            self.model_dir = model_dir
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_latest_model_path(self):
        try:
            folder_name = list(map(int, os.listdir(self.model_dir)))
            latest_model_dir = os.path.join(self.model_dir, f"{max(folder_name)}")
            file_name = os.listdir(latest_model_dir)[0]
            latest_model_path = os.path.join(latest_model_dir, file_name)
            return latest_model_path
        except Exception as e:
            raise CustomException(e, sys) from e

    def predict(self, X):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            concrete_compressive_strength = model.predict(X)
            return concrete_compressive_strength
        except Exception as e:
            raise CustomException(e, sys) from e