import csv



class parameter_creator:
    def get_params(self, csv_location):
        fields = []
        rows = []
        with open(csv_location, 'r') as csvfile:

            csvreader = csv.reader(csvfile)

            fields = next(csvreader)
            for row in csvreader:
                rows.append(row)

            print('# of rows: %d'%(csvreader.line_num))

        print('field names are:' + ', '.join(field for field in fields))
        print('\nFirst 5 rows are:\n') 
        for row in rows[:5]: 
            # parsing each column of a row 
            for col in row: 
                print("%10s"%col), 
            print('\n') 

    def __init__(self, csv_location):
        self.get_params(csv_location)


parameters = parameter_creator("test.csv")
