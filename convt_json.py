import json

# the file to be converted to 
# json format
filename = 'data.txt'

# dictionary where the lines from
# text will be stored
dict1 = {}

# creating dictionary
with open(filename) as fh:
    for line in fh:
        # strip leading/trailing spaces
        line = line.strip()

        # skip empty lines
        if not line:
            continue

        # try to split the line into two parts
        try:
            command, description = line.split(None, 1)
            dict1[command] = description.strip()
        except ValueError:
            # if line doesn't split into 2 parts, skip it
            continue

# creating json file
# the JSON file is named as test1
with open("data.json", "w") as out_file:
    json.dump(dict1, out_file, indent=4, sort_keys=False)
