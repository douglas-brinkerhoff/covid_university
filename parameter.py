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
        for row in self.rows:
            # parsing each column of a row 
               if len(row) > 2:
                   if row[2] == 'bool':
                       row[1] = ('True' == row[1])
                   if row[2] == 'int':
                       row[1] = float(row[1])
                      
    
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



parameters = parameter_creator("test.csv")
print("dict; ", parameters.dict_parameters)
