import numpy as np
import pandas as pd

from typing import Tuple, Union, List

from datetime import datetime
def get_period_day(date):
    date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
    morning_min = datetime.strptime("05:00", '%H:%M').time()
    morning_max = datetime.strptime("11:59", '%H:%M').time()
    afternoon_min = datetime.strptime("12:00", '%H:%M').time()
    afternoon_max = datetime.strptime("18:59", '%H:%M').time()
    evening_min = datetime.strptime("19:00", '%H:%M').time()
    evening_max = datetime.strptime("23:59", '%H:%M').time()
    night_min = datetime.strptime("00:00", '%H:%M').time()
    night_max = datetime.strptime("4:59", '%H:%M').time()
    
    if(date_time > morning_min and date_time < morning_max):
        return 'mañana'
    elif(date_time > afternoon_min and date_time < afternoon_max):
        return 'tarde'
    elif(
        (date_time > evening_min and date_time < evening_max) or
        (date_time > night_min and date_time < night_max)
    ):
        return 'noche'

def is_high_season(fecha):
    fecha_año = int(fecha.split('-')[0])
    fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
    range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year = fecha_año)
    range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year = fecha_año)
    range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year = fecha_año)
    range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year = fecha_año)
    range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year = fecha_año)
    range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year = fecha_año)
    range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year = fecha_año)
    range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year = fecha_año)
    
    if ((fecha >= range1_min and fecha <= range1_max) or 
        (fecha >= range2_min and fecha <= range2_max) or 
        (fecha >= range3_min and fecha <= range3_max) or
        (fecha >= range4_min and fecha <= range4_max)):
        return 1
    else:
        return 0

def get_min_diff(data):
    fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
    fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
    min_diff = ((fecha_o - fecha_i).total_seconds())/60
    return min_diff

class DelayModel:

    def __init__(
        self
    ):
        self._model = None # Model should be saved in this attribute.
        self._scale = None
        self._dtype = {
            'Fecha-I': str, #Scheduled date and time of the flight
            'Vlo-I': str, #Scheduled flight number, int but can have string value
            'Ori-I': str, #Programmed origin city code
            'Des-I': str, #Programmed destination city code
            'Emp-I': str, #Scheduled flight airline code
            'Fecha-O': str, #Date and time of flight operation
            'Vlo-O': str, #Flight operation number of the flight, int but can have empty value
            'Ori-O': str, #Operation origin city code
            'Des-O': str, #Operation destination city code
            'Emp-O': str, #Airline code of the operated flight
            'DIA': int, #Day of the month of flight operation
            'MES': int, #Number of the month of operation of the flight
            'AÑO': int, #Year of flight operation
            'DIANOM': str, #Day of the week of flight operation
            'TIPOVUELO': str, #Type of flight, I =International, N =National
            'OPERA': str, #Name of the airline that operates
            'SIGLAORI': str, #Name city of origin
            'SIGLADES': str, #Destination city name
        }
    
    def pickle_train(self) -> None:
        data = pd.read_csv(filepath_or_buffer="data/data.csv", dtype=self._dtype)
        features, target = self.preprocess(data, 'delay')
        self.fit(features, target)
        
        import pickle
        # save the model to a file
        with open("challenge/model.pkl", "wb") as f:
            pickle.dump(self._model, f)
    
    def pickle_load(self) -> None:
        import pickle
        with open("challenge/model.pkl", "rb") as f:
            self._model = pickle.load(f)
        self._scale = 55592 / 12614

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        # sep=',', encoding='utf-8', dtype=dtype
        # data = pd.read_csv('../data/data.csv', dtype=self._dtype)
        
        # data['period_day'] = data['Fecha-I'].apply(get_period_day)
        # data['high_season'] = data['Fecha-I'].apply(is_high_season)
        
        features = pd.concat([
            pd.get_dummies(data['OPERA'], prefix = 'OPERA'),
            pd.get_dummies(data['TIPOVUELO'], prefix = 'TIPOVUELO'), 
            pd.get_dummies(data['MES'], prefix = 'MES')], 
            axis = 1
        )
        
        top_10_features = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]
        
        if target_column:
            if not target_column in data:
                if not 'min_diff' in data:
                    data['min_diff'] = data.apply(get_min_diff, axis = 1)
                
                threshold_in_minutes = 15
                data[target_column] = np.where(data['min_diff'] > threshold_in_minutes, 1, 0)
            
            target = data[[target_column]] # delay
            target_counts = target[target_column].value_counts()
            self._scale =  target_counts[0] / target_counts[1]
            #return features[top_10_features], target
            return features.T.reindex(top_10_features).T.fillna(0), target
        
        return features.T.reindex(top_10_features).T.fillna(0)

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        import xgboost as xgb
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01, scale_pos_weight = self._scale)
        self._model.fit(features, target)
        return

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """
        if self._model is None:
            self.pickle_load()
        
        y_preds = self._model.predict(features)
        return [1 if y_pred > 0.5 else 0 for y_pred in y_preds]

