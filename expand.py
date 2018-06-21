import csv
import sys
import json

data = []

maxInt = sys.maxsize
decrement = True
while decrement:
    try:
        csv.field_size_limit(maxInt)
        decrement = False
    except OverflowError:
        maxInt = int(maxInt / 2)

def read_data(filename):
	global data
	csv_file = open(filename, 'r', encoding='utf-8')
	csv_reader = csv.reader(csv_file)
	for line in csv_reader:
		data.append(line)
	csv_file.close()

def header_row():
	global data
	header_row = 0
	while header_row < len(data) and data[header_row] != []:
		header_row += 1
	header_row += 1
	if header_row >= len(data):
		header_row = 0
	return header_row

def json_keys(cell):
	try:
		int(cell)
		return None
	except ValueError:
		pass
	try:
		float(cell)
		return None
	except ValueError:
		pass
	try:
		return list(json.loads(cell)[0].keys())
	except ValueError:
		return None

def find_json_columns(range_start, range_end):
	global data, header_row
	json_columns = {}
	for column in range(range_start, range_end):
		row = header_row + 1

		while row < len(data):
			try:
				if data[row][column] == None or data[row][column] == '':
					row += 1
				else:
					break
			except:
				row += 1

		if row == len(data):
			continue

		keys = json_keys(data[row][column])
		if keys != None:
			json_columns[column] = keys
	return json_columns


def fix_json_columns(range_start, range_end):
	global data, header_row

	json_columns = find_json_columns(range_start, range_end)

	cols_added = 0

	for column in json_columns.keys():
		adj_col = column + cols_added
		header_keys = []
		for header in json_columns[column]:
			header_keys.append(data[header_row][adj_col] + '_' + header)
		data[header_row] = data[header_row][:adj_col] + header_keys + data[header_row][adj_col + 1:]

		new_data = []
		for row in range(header_row + 1, len(data)):
			if data[row][adj_col] == None or data[row][adj_col] == '':
				empty_cells = [None] * len(json_columns[column])
				new_data.append(data[row][:adj_col] + empty_cells + data[row][adj_col + 1:])
				continue
			cell_data = json.loads(data[row][adj_col])
			for item in cell_data:
				new_row = data[row][:adj_col]
				for key in json_columns[column]:
					if type(item[key]) == list:
						new_row += [json.dumps(item[key])]
					else:
						new_row += [item[key]]
				new_row += data[row][adj_col + 1:]
				new_data.append(new_row)

		data = data[:header_row + 1] + new_data

		cols_added += fix_json_columns(column, column + len(json_columns[column]))
		cols_added += len(json_columns[column]) - 1

	return cols_added

def new_filename(filename):
	name_parts = filename.split('.')
	if len(name_parts) == 1:
		name_parts[0] += '_expanded'
	else:
		name_parts[-2] += '_expanded'
	return '.'.join(name_parts)

def write_data(new_filename):
	global data
	expanded = open(new_filename, 'w', encoding='utf-8', newline='')
	csv_writer = csv.writer(expanded)
	for line in data:
		csv_writer.writerow(line)
	expanded.close()

def expand(filename):
	global data, header_row

	print('Reading data from %s...' % (filename))
	read_data(filename)
	header_row = header_row()

	print('Expanding columns with json data...')
	fix_json_columns(0, len(data[header_row]))

	new_file = new_filename(filename)
	print('Writing data to %s...' % (new_file))
	write_data(new_file)

	print('Done!')	

filename = sys.argv[1]
expand(filename)