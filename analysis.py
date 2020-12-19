import json
from sklearn.metrics import mean_squared_error
import numpy as np




class analyzer:
    def __init__(self,keys): 
        self.values = {}   



        #crutch for linking names of data with dict
        self.data_names = [('daily_positive','positive_tests_total'), ('daily_testing', 'tests_performed_total')]
        # end crutch will remove



        parameters = None 
        # initialize empty dictionary for all keys
        for key in keys:
            self.values[key] = {}
    def record(self,recorded_info):
         
        for key in self.values.keys():
            totals = [ run_num[key] for run_num in recorded_info ] 
            totals = np.array(totals)
            self.values[key]['all_runs'] = totals 
    def show_values(self):
        for key in self.values.keys():
            
            print('$'*40)
            print(key)
            print(self.values[key])
            print('$'*40)
    
    # for multiple runs will combine all data for average
    def find_means(self):
        for key in self.values.keys():
            self.values[key]['mean'] = np.mean(self.values[key]['all_runs'], axis=0, dtype=np.float32)

    def mse(self):
        ## will writer for this part later
        json_dict = {} 
        #load actual data from UM
        with open('data.txt','r') as j_file:
           json_dict = json.load(j_file) 
        ## end writer
        for data_name, key in self.data_names:
            cummulative = []
            #get cummulative for given day 
            for index, val in enumerate(json_dict[data_name][86:]):
                summed = val
                if index != 0:
                   summed+=cummulative[index-1] 
                cummulative.append(summed) 
            mse = mean_squared_error(cummulative, self.values[key]['mean'])
            self.values[key]['mse'] = mse
             

        

class h5writer:
    def __init__(self, filename):
        self.file = filename



