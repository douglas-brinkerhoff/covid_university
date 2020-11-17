import csv



class parameter_creator:
    def get_params(self, csv_location):
        self.fields = []
        self.rows = []
        with open(csv_location, 'r') as csvfile:

            csvreader = csv.reader(csvfile)

            self.fields = next(csvreader)
            for row in csvreader:
                self.rows.append(row)

            print('# of rows: %d'%(csvreader.line_num))

        print('field names are:' + ', '.join(field for field in self.fields))
        print('\nFirst 5 rows are:\n') 
        for row in self.rows[:5]: 
            # parsing each column of a row 
            for col in row: 
                print("%10s"%col), 
            print('\n') 

    
    def dict_convert(self):
        for row in self.rows:
           self.dict_parameters[row[0]] = row[1]


    def __init__(self, csv_location):
        self.fields = []
        self.rows = []
        self.get_params(csv_location)
        self.dict_parameters = {}
        self.dict_convert()



parameters = parameter_creator("parameters.csv")
print("dict; ", parameters.dict_parameters)
