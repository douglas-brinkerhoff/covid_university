import csv
import ast



class parameter_creator:
    def get_params(self, csv_location):
        self.fields = []
        self.rows = []
        with open(csv_location, 'r') as csvfile:

            csvreader = csv.reader(csvfile)

            self.fields = next(csvreader)
            for row in csvreader:
                self.rows.append(row)
        print(len(self.rows))
        for row in self.rows:
            # parsing each column of a row 
            if row[1] != '': 
                row[1] = ast.literal_eval(row[1])            

    
    def dict_convert(self):
        for row in self.rows:
           value = ''
           self.dict_parameters[row[0]] = row[1]



    def __init__(self, csv_location):
        self.fields = []
        self.rows = []
        self.get_params(csv_location)
        self.dict_parameters = {}
        self.dict_convert()



parameters = parameter_creator("parameters.csv")
print("dict; ", parameters.dict_parameters)
