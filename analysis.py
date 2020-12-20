import json
from sklearn.metrics import mean_squared_error
import numpy as np
import h5py


class analyzer:
    def __init__(self,keys): 
        '''
        format is as such: list['keys'] -> dictionary{'all_runs'# raw run data,
        'mean'#mean of all run values for given day, 
        'mse # value of mse '} 
        '''
        self.values = {}   

        #crutch for linking names of data with dict
        self.data_names = [('daily_positive','positive_tests_total'), ('daily_testing', 'tests_performed_total')]
        # end crutch will remove

        # parameters set in pandemic during init
        parameters = None 

        # initialize empty dictionary for all keys
        for key in keys:
            self.values[key] = {}



    #specific set of runs recorder.all_records passed here. 
    def record(self,recorded_info):
        # recorded_info in format list[dictionarys] 
        for key in self.values.keys():
            # get specific items list from each individual run 
            totals = [ run_num[key] for run_num in recorded_info ] 
            totals = np.array(totals)
            self.values[key]['all_runs'] = totals 


    def show_values(self):
        print('^' * 50)
        print(self.parameters)
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
        ## will have writer for this part later
        json_dict = {} 
        #load actual data from UM
        with open('data.txt','r') as j_file:
           json_dict = json.load(j_file) 
        ## end writer
        for data_name, key in self.data_names:
            cummulative = []
            #get cummulative for given day in actual data
            for index, val in enumerate(json_dict[data_name][86:]):
                summed = val
                if index != 0:
                   summed+=cummulative[index-1] 
                cummulative.append(summed) 

            
            mse = mean_squared_error(cummulative, self.values[key]['mean']) 
            self.values[key]['mse'] = mse
    
    def store(self, file_name):
        # storing of the parameters for reset?
        

class h5writer:
    def __init__(self, filename):
        self.file = filename
        self.current_gen = 'gen_1'  
        self.create_hdf5()

    def create_hdf5(self):
        #create file, fails if exists
        try:
            with h5py.File(self.file, 'x') as f: 
                f.create_group(self.current_gen) 

        # except for when file already exists
        except OSError:
            with h5py.File(self.file, 'r') as f:
                # if file exists get latest generation value
                self.current_gen = list(f.keys())[-1]


    # new group in the file
    def create_new_gen(self):
        with h5py.File(self.file, 'r+') as f:
            #get current gen num value and increment
            num = int(self.current_gen[-1])+1

            f.create_group('gen_'+str(num)) 

            # set current gen value to newest created
            self.current_gen = 'gen_'+str(num) 
    def store_analysis(self, analysis):
        mse_list = []
        with h5py.File(self.file, 'r+') as f:
            # get file location of the current generation

            f_gen = f[self.current_gen]
            # create new group for current run, named by scenario name
            f_scenario = f_gen.create_group(analysis.parameters['scenario_name'])
            # convert dict to tuple list for np.array to use
            tuple_list = list(analysis.parameters.items())
            f_scenario.create_dataset('parameters', data=np.array(tuple_list))
            
            f_data = f_scenario.create_group('data')
            for key in analysis.values.keys():
                # add the key and mse pair to mse_list for later storing
                mse_list.append((key, analysis.values[key]['mse']))

                # storing all runs dataset /gen/scenario/data/all_runs
                f_data.create_dataset('all_runs', data= analysis.values[key]['all_runs'])

                #storing mean dataset /gen/scenario/data/mean
                f_data.create_dataset('mean', data=analysis.values[key]['mean'])
            
            # add the mse_list /gen/scenario/mse
            f_scenario.create_dataset('mse', data=np.array(mse_list))

# for testing
if __name__ == '__main__':
    writer = h5writer('test.hdf5')
    writer.create_hdf5()
    print(writer.current_gen)
    f = h5py.File('test.hdf5', 'r+')
    print(list(f.keys()))
    test = f['gen_1']['test'] 
    print(test.name)
    f.close()
