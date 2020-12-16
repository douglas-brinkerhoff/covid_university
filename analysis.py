import numpy as np




class analyzer:
    def __init__(self,keys): 
        self.keys = keys 
        self.values = {}   
    
    def record(self,recorded_info):
         
        for key in self.keys:
            totals = [ run_num[key] for run_num in recorded_info ] 
            print('#'*40)
            print(totals)
            print('#'*40)
            totals = np.array
