import json

filename = input('enter file to be converted: ')
filename_stored = input('enter where to store: ')

# param.txt file has correct param typings
with open('param.txt') as F:
    correct_param = json.load(F)




with open(filename, 'r') as F:
    data = json.load(F)

for key, value in data.items():
    if isinstance(correct_param[key]['mean'], int):
        # properly rounds ints
        print(key)
        print('parameter before round', value)
        value = round(value, 0)
        value = int(value)
        if isinstance(correct_param[key]['mean'], bool):
            value = bool(value)

        print('parameter after round', value)
        print('*'*30)
    # reuse old format since it has correct max and min values as well
    correct_param[key]['mean'] = value
    correct_param[key]['std_dev'] = 0


with open(filename_stored, 'w') as F:
    json.dump(correct_param, F, indent=4) 


print('successfully converted')

