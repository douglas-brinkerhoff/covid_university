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
                self.dict_params[key] = sample_val

            # if bool then sample bernoulli instead of normal
            if isinstance(value['mean'], bool):
                bern = stats.bernoulli(value['std_dev'])

                sample_val = (0 != bern.rvs(size=1)[0])
                self.dict_params[key] = sample_val


        print(self.dict_params)
        return self.dict_params

    
           
    def __init__(self, json_file):
        self.json_file = json_file
        self.dict_params = {}
        self.dict_dist = {}
        self.get_params_dist()


parameters = parameter_creator("param.txt")
parameters.randomized_sample()
