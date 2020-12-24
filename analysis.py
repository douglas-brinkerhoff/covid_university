import json
from sklearn.metrics import mean_squared_error
import numpy as np
import h5py


class analyzer:
    def __init__(self,keys): 
        #init and save hd writer
        self.writer = h5writer('output.hdf5')
        '''
        format is as such: list['keys'] -> dictionary{'all_runs'# raw run data,
        'mean'#mean of all run values for given day, 
        'mse # value of mse '} 
        '''
        self.values = {}   


        # parameters set in pandemic during init
        self.parameters = None 


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

        # on record calculate that runs mean and mse
        self.find_means()
        self.mse()
        self.store()

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
           for key in self.values.keys():             

               mse = mean_squared_error(json_dict[key], self.values[key]['mean']) 
               self.values[key]['mse'] = mse
    
    def store(self):
        # storing of the parameters for reset?
        self.writer.store_analysis(self)         

class h5writer:
    def __init__(self, filename):
        self.file = filename
        self.create_hdf5()

    def create_hdf5(self, new_gen=True):
        #create file, fails if exists
        try:
            with h5py.File(self.file, 'x') as f: 
                f.create_group('gen_1') 
                #give the file metadata on what generation its on
                f.attrs['gen'] = 1

        # except for when file already exists
        except OSError:
           #if new_gen option true then create new generation group
            if new_gen:
                self.create_new_gen()


    # new group in the file
    def create_new_gen(self):
        with h5py.File(self.file, 'r+') as f:
            #get current gen num value and increment
            file_gen = f.attrs['gen']+1 
            f.create_group('gen_'+str(file_gen))
            #increment the generation in the file
            f.attrs['gen'] = file_gen
    
    '''
    data in format

    -gen#
     |--trial# 
        |--mse (stored as string_ json to unpack)
        |--parameters (stored at string json to unpack)
        |--data
           |--dataname
              |--all_runs (list of lists storing all run data)
              |--mean (mean of all run data)
    '''
    def store_analysis(self, analysis):
        print('## storing for analysis ##')
        mse_list = []
        with h5py.File(self.file, 'r+') as f:
            # get file location of the current generation
            generation = f.attrs['gen']
            f_gen = f['gen_' + str(generation)]

            # create new group for current run, named by scenario name
            f_scenario = f_gen.create_group(analysis.parameters['scenario_name'])
            # convert dict to tuple list for np.array to use
            tuple_list = json.dumps(analysis.parameters)
            f_scenario.create_dataset('parameters', data=np.array(tuple_list, dtype='S'))
            
            f_data = f_scenario.create_group('data')

            for key in analysis.values.keys():
                #create folder for specific key
                f_specific = f_data.create_group(key)
                # add the key and mse pair to mse_list for later storing
                mse_list.append((key, analysis.values[key]['mse']))

                # storing all runs dataset /gen/scenario/data/$key/all_runs
                f_specific.create_dataset('all_runs', data= analysis.values[key]['all_runs'])

                #storing mean dataset /gen/scenario/data/$key/mean
                f_specific.create_dataset('mean', data=analysis.values[key]['mean'])
            
            # add the mse_list /gen/scenario/mse
            f_scenario.create_dataset('mse', data=np.array(mse_list ,dtype='S'))
        print('## successfully stored for analysis ##')

# for testing
if __name__ == '__main__':
    f = h5py.File('output.hdf5', 'r')
    def recursive_file(name):
        print(name)

    f.visit(recursive_file)
    print('attrs', list(f.attrs.keys()))
    def print_recursive(name, object):
        if 'mse' in name:
            print(name)
            print(object[...])
    
    f.visititems(print_recursive)
    f.close()
