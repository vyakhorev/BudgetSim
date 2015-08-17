# -*- coding: utf-8 -*-

from shared import *

class c_simulation_results_container():
    #Одна на эпоху - быстрый лог данных с последующим преобразованием в dataframe
    def __init__(self):
        self.ts_dict = {}
    
    def __repr__(self):
        s = "c_simulation_results_container:" + "\n"
        for k_obs_i in self.ts_dict.iterkeys():
            s += "--data from " + k_obs_i + "\n"
            ts_i = self.ts_dict[k_obs_i]
            for k_ts_i in ts_i.iterkeys():
                s += "----data of " + k_ts_i + "\n"
                s += ts_i[k_ts_i].__repr__()
        return s
    
    def add_ts_point(self, observer_name, ts_name, timestamp, value):
        # Точка входа для Observer - единственный способ добавить данные об эпохе
        observer_name = unicode(observer_name)
        ts_name = unicode(ts_name)
        if not(self.ts_dict.has_key(observer_name)):
            self.ts_dict[observer_name] = dict()
        if not(self.ts_dict[observer_name].has_key(ts_name)):
            self.ts_dict[observer_name][ts_name] = c_fast_ts()
        self.ts_dict[observer_name][ts_name].add_obs(timestamp, value)
        
    def get_sim_results(self, observer_name, ts_name):
        try: 
            return self.ts_dict[observer_name][ts_name]
        except KeyError:
            return None
    
    def get_available_names(self):
        my_keys = []
        for k1 in self.ts_dict.keys():
            for k2 in self.ts_dict[k1]:
                my_keys.append([k1, k2])
        return my_keys
    
    def get_dataframe_for_epochvar(self, observer_name, variable_name):
        #Это для формы с результатом по эпохе
        datas_4_pandas = dict()
        datas_4_pandas[variable_name] = self.get_sim_results(observer_name,variable_name).return_series()
        df = pd.DataFrame(datas_4_pandas)
        return df

class c_fast_ts():
    # Используется во время симуляции для сбора данных
    def __init__(self):
        self.timestamps = []
        self.values = []

    def __repr__(self):
        s = "c_fast_ts:" + "\n"
        for k in range(0,len(self.timestamps)):
            s += str(self.timestamps[k]) + " : " + str(self.values[k]) + "\n"
        return s

    def __len__(self):
        return len(self.timestamps)

    def add_obs(self, timestamp, value):
        self.timestamps.append(timestamp)
        self.values.append(value)

    def return_series(self, start_date = 0):
        #start_date может быть DateTime
        tempdict = dict()
        for k in range(0,len(self.values)):
            # В режиме симуляции мы храним отсчет в днях и при финальной обработке переводим в даты
            # Однако в иных случаях используем класс просто с временными метками (обычно дата)
            if start_date == 0:
                d = self.timestamps[k]
            else:  #д.б. datetime
                d = start_date + datetime.timedelta(days=self.timestamps[k])
            if tempdict.has_key(d):
                tempdict[d] += self.values[k]
            else:
                tempdict[d] = self.values[k]
        Panda_Series = pd.Series(tempdict)
        return Panda_Series


def __uniq(input): #Ы?
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output        


# Это отдельно - не для хранения, для симуляции

# class c_event_predictive_ts():
#     # Используются для простых предсказаний событий.
#     # Когда, сколько, с.к.о. когда, с.к.о. сколько.
#     def __init__(self):
#         self.data_ts = c_fast_ts()
#         self.prediction_value_expectation = 0
#         self.prediction_value_std = 0
#         self.prediction_timedelta_expectaion = 0
#         self.prediction_timedelta_std = 0
#         self.last_event_date = None
#
#     def __repr__(self):
#         return unicode(self.data_ts.return_series())
#
#     def add_point(self, timestamp, value):
#         self.data_ts.add_obs(timestamp, float(value))
#
#     def run_estimations(self):
#         ts = self.data_ts.return_series()
#         if len(ts) >= 3:  #Минимум три наблюдений в разные даты
#             self.prediction_value_expectation = round(numpy.average(ts.values))
#             self.prediction_value_std = round(numpy.std(ts.values))
#             ts_d = []
#             ts_td = numpy.diff(ts.keys().tolist())
#             for td in ts_td:
#                 ts_d += [td.days]
#             self.prediction_timedelta_expectaion = round(numpy.mean(ts_d))
#             self.prediction_timedelta_std = round(numpy.std(ts_d))
#             self.last_event_date = max(self.data_ts.timestamps)