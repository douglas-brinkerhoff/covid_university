import json
from sklearn.metrics import mean_squared_error
import numpy as np
import h5py


class recorder:
    def __init__(self,keys): 
        #init and save hd writer
        self.writer = h5writer('full_data.hdf5')
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
            print('new generation #', file_gen, ' started', flush=True)
            f.attrs['gen'] = file_gen
    
    '''
    data in format

    -gen_#
     |--trial_# 
        |--mse (stored as string_ json to unpack)
        |--parameters (stored at string json to unpack)
        |--data
           |--dataname
              |--all_runs (list of lists storing all run data)
              |--mean (mean of all run data)
    '''
    def store_analysis(self, analysis):
        print('## storing for analysis ##')
        mse_dict = {}
        
        with h5py.File(self.file, 'r+') as f:
            # get file location of the current generation
            generation = f.attrs['gen']
            f_gen = f['gen_' + str(generation)]

            # create new group for current run, named by scenario name
            f_scenario = f_gen.create_group(analysis.parameters['scenario_name'])
            # convert dict to tuple list for np.array to use
            json_parameters = json.dumps(analysis.parameters)
            f_scenario.create_dataset('parameters', data=np.array(json_parameters, dtype='S'))
            
            f_data = f_scenario.create_group('data')

            for key in analysis.values.keys():
                #create folder for specific key
                f_specific = f_data.create_group(key)
                # add the key and mse pair to mse_dict for later storing
                mse_dict[key] = analysis.values[key]['mse']

                # storing all runs dataset /gen/scenario/data/$key/all_runs
                f_specific.create_dataset('all_runs', data= analysis.values[key]['all_runs'])

                #storing mean dataset /gen/scenario/data/$key/mean
                f_specific.create_dataset('mean', data=analysis.values[key]['mean'])
            
            # convert mse_dict to json format then store the string
            #add the mse_dict /gen/scenario/mse
            f_scenario.create_dataset('mse', data=np.array(json.dumps(mse_dict) ,dtype='S'))
        print('## successfully stored for analysis ##', flush=True)


class loader:
    def __init__(self, hdf5_file):
       self.data_file  = hdf5_file
       # mse and param in format [{mse:, param:},]
       self.mse_pairs = [] 
       self.all_data = {}
    def generate_mse_pairs_file(self):
       with h5py.File(self.data_file, 'r') as f:
 
            # iterate through all the generations
            for f_gen_name in f.__iter__():
                '__iter__ returns name so must convert to file'
                f_gen = f[f_gen_name]
            #iterate through all trail_# for given gen
                for num, trail in enumerate(list(f_gen.keys())):
                    #get file object for trail folder
                    f_trail = f_gen[trail]
                    # get serialized json data back to normal form
                    mse  = json.loads(f_trail['mse'][...].tolist())
                    parameters = json.loads(f_trail['parameters'][...].tolist())
                    
                    # add new dictionarys to mse_pairs list
                    self.mse_pairs.append({'mse': mse, 
                                           'parameters': parameters }
                                           )
                #store current gen
                self.reset(f_gen_name)



    def reset(self, gen):
        # check if any values are in mse_pairs
        # if yes then store values in the all_data
        
        if self.mse_pairs:
            self.all_data[gen] = self.mse_pairs
            # reset array
            self.mse_pairs = []
 
    def mse_find(self, num=1):
        #find largest  
        mse_pairs_arr = np.array([])
        for gen in self.all_data.keys():
            gen = self.all_data[gen]
            for pairs in gen:
               'get the mse values'
               temp_pair = np.array(list(pairs['mse'].values()))
               # if mse_pairs has no values then set it equal to first value
               if mse_pairs_arr.size == 0:
                   mse_pairs_arr = temp_pair
               # else vertical append new values
               else:
                   mse_pairs_arr = np.vstack((mse_pairs_arr, temp_pair))
        location_mins = np.argmin(mse_pairs_arr, axis=0)
        print(location_mins)
        print(mse_pairs_arr[location_mins[0]], mse_pairs_arr[location_mins[1]])
 
        return location_mins

# for testing
if __name__ == '__main__':
    print('\n'*3)
    print('#'*40)
    with h5py.File('full_data.hdf5','r') as f:
        print(list(f['gen_20'].keys()))
        print(list(f['gen_20/trial_301/data/active_cases/mean'][...]))
    '''
    obj_analyzer = loader('output_new_format.hdf5')
    obj_analyzer.generate_mse_pairs_file()
    f = h5py.File('output_new_format.hdf5', 'r')
    def get_parameters_small():
        smallest = obj_analyzer.mse_find()
        counter = 0
        def find_smallest(name, object):
            nonlocal counter
            if 'mse' in name:
                print(name, object[...]) 
                if counter in smallest:
                    print(name)
                    print(object[...])
                counter += 1 
        f.visititems(find_smallest)

    #get_parameters_small()
    f.close()
    ''' 



