import json
import scipy.stats as stats


class parameter_creator:
    # get mean and std deviation from json file into dict
    def get_params_dist(self):
        with open(self.json_file, 'r') as j_file:
            self.dict_dist = json.load(j_file)
            

    def update_json_file(self, dictionary):
        with open(self.json_file, 'w') as json_file:
            json.dump(dictionary, json_file, sort_keys=True, indent=4, separators=(',', ': '))

    
    def fully_randomized_sample(self):
        for key, value in self.dict_dist.items():
            
            if isinstance(value['mean'], (int, float)) and not isinstance(value['mean'], bool): # must clarify bool as bool is subclass of int
                randomized =2*(stats.beta.rvs(2, 2, size=1)[0])
                randomized *= value['mean'] 
                

                if isinstance(value['mean'], int):
                    randomized = int(randomized)

                # when fully randomized values can be illegal
                if 'min_val' in value and randomized < value['min_val']:
                    randomized = value['min_val']
            
                if 'max_val' in value and randomized > value['max_val']:
                    randomized = value['max_val']


                self.dict_params[key] = randomized
            if isinstance(value['mean'], bool):
                random_percent = stats.beta.rvs(2,2,size=1)[0]
                bern = stats.bernoulli(random_percent)

                random_val = bool((0 != bern.rvs(size=1)[0]))
                self.dict_params[key] = random_val
        self.dict_params['scenario_name'] = 'trial_'+str(self.run_num)

        self.run_num += 1
        return self.dict_params

    def randomized_sample(self):
        for key, value in self.dict_dist.items():
            if isinstance(value['mean'], (int, float)) and not isinstance(value['mean'], bool): # must clarify bool as bool is subclass of int
                
                # setup normal distribution
                norm = stats.norm(value["mean"], # mean
                                  value['std_dev']
                           )

                # sample normal 
                sample_val = norm.rvs(size=1)[0]
                sample_val = float('%.3f' % sample_val)  # makes values only have 3 decimal points for neatness

                # convert value to int if original was an int
                if isinstance(value['mean'], int):
                    # if mean is int verify that it remains that way
                     sample_val = int(sample_val)


                if 'max_val' in value and sample_val > value['max_val']:
                    sample_val = value['max_val']

                #negative values do not make sense for any of the values and thus cannot happen
                
                if sample_val < 0:
                    sample_val = 0
          



                self.dict_params[key] = sample_val

            # if bool then sample bernoulli instead of normal
            if isinstance(value['mean'], bool):
                percent=value['std_dev'] if value['mean'] == False else 1-value['std_dev']  
                bern = stats.bernoulli(percent)

                sample_val = bool((0 != bern.rvs(size=1)[0]))
                self.dict_params[key] = sample_val

        self.dict_params['scenario_name'] = 'trial_'+str(self.run_num) 
        self.run_num += 1
        return self.dict_params
    
    
           
    def __init__(self, json_file):
        self.run_num = 1
        self.json_file = json_file
        self.dict_params = {}
        self.dict_dist = {}
        self.get_params_dist()


