import re

__all__ = ['read_photometry_ticket', 'read_spectra_ticket', 'read_spectra_metadata']

def read_photometry_ticket(contents):
	""" Reads photometry ticket
		Returns tuple of dictionaries (value_dict, column_dict)
	"""	
	
	value_dict, column_dict = {}, {}
	ticket_fields = ["OBJECT NAME: ", "TIME UNITS: ", "FLUX UNITS: ",  "FLUX ERROR UNITS: ", "FILTER SYSTEM: ", "MAGNITUDE SYSTEM: ", "WAVELENGTH REGIME: ", "TIME SYSTEM: ", "ASSUMED DATE OF OUTBURST: ", "TELESCOPE: ", "OBSERVER: ", "REFERENCE: ", "BIBCODE: ", "DATA FILENAME: ", "TIME COLUMN NUMBER: ", "FLUX COLUMN NUMBER: ", "FLUX ERROR COLUMN NUMBER: ", "FILTER/FREQUENCY/ENERGY RANGE COLUMN NUMBER: ", "UPPER LIMIT FLAG COLUMN NUMBER: ", "TELESCOPE COLUMN NUMBER: ", "OBSERVER COLUMN NUMBER: ", "FILTER SYSTEM COLUMN NUMBER: ", "TICKET STATUS: "]
	
	lines = contents.split("\n")
	
	j = 0
	for i in range(len(lines)):
		name_match = re.match(ticket_fields[j], lines[i])
		if name_match:
			value = lines[i][name_match.end():].strip()
			key = ticket_fields[j][:-2]
			if key.endswith(' COLUMN NUMBER'):
				key = key[:-14]
				try: column_dict[key] = int(value)
				except ValueError: column_dict[key] = None
			else:
				if value.upper() == 'NA' or value == '': value_dict[key] = None
				else: value_dict[key] = value
		j+=1
		if j == len(ticket_fields): break
		

	if len(value_dict) + len(column_dict) != len(ticket_fields):
		
		raise AttributeError('Not a valid ticket.')
	
	return (value_dict, column_dict)


def read_spectra_ticket(contents):
	""" Reads spectra ticket, returns dictionary
	"""	
	value_dict, column_dict = {}, {}
	ticket_fields = ["OBJECT NAME: ", "FLUX UNITS: ", "FLUX ERROR UNITS: ", "WAVELENGTH REGIME: ", "TIME SYSTEM: ", "ASSUMED DATE OF OUTBURST: ", "REFERENCE: ", "BIBCODE: ", "DEREDDENED FLAG: ", "METADATA FILENAME: ", "FILENAME COLUMN: ", "WAVELENGTH COLUMN: ", "FLUX COLUMN: ", "FLUX ERROR COLUMN: ", "FLUX UNITS COLUMN: ", "DATE COLUMN: ", "TELESCOPE COLUMN: ", "INSTRUMENT COLUMN: ", "OBSERVER COLUMN: ", "SNR COLUMN: ", "DISPERSION COLUMN: ", "RESOLUTION COLUMN: ", "WAVELENGTH RANGE COLUMN: ", "TICKET STATUS: "]

	lines = contents.split("\n")

	j = 0
	for i in range(len(lines)):
		name_match = re.match(ticket_fields[j], lines[i])
		if name_match:
			value = lines[i][name_match.end():].strip()
			key = ticket_fields[j][:-2]
			if key.endswith(' COLUMN'):
				key = key[:-7]
				if key == 'WAVELENGTH RANGE':
					try:					
						v1, v2 = tuple([x.strip() for x in value.split(',')][:2])					
						column_dict[key + ' 1'] = int(v1)
						column_dict[key + ' 2'] = int(v2)
					except (IndexError, ValueError):
						column_dict[key + ' 1'] = None
						column_dict[key + ' 2'] = None
				else:
					try: column_dict[key] = int(value)
					except ValueError: column_dict[key] = None
			else:
				value_dict[key] = value
		j+=1
		if j == len(ticket_fields): break

	if len(value_dict) + len(column_dict) != len(ticket_fields) + 1:
		raise AttributeError('Not a valid ticket.')

	return (value_dict, column_dict)

def read_spectra_metadata(contents, col_num_dict):
	
	metadata_fields = ['FILENAME', 'WAVE COL NUM', 'FLUX COL NUM', 'FLUX ERR COL NUM', 'FLUX UNITS', 'DATE', 'OBSERVER', 'TELESCOPE', 'INSTRUMENT', 'SNR', 'DISPERSION', 'RESOLUTION', 'WAVE RANGE 1', 'WAVE RANGE 2']


	lines = contents.split("\n")
	lines = [line.split(",") for line in lines]
	k = 0
	for i in range(len(lines)):
		if lines[i][0].startswith("#"):
			lines[i][0] = lines[i][0][1:]
			k += 1
		else:
			break
	k = 1

	file_list = []
	for i in range(k, len(lines)):
		value_dict, column_dict = {}, {}
		for field_name in col_num_dict:
			if col_num_dict[field_name] is None: continue

			value = lines[i][col_num_dict[field_name]].strip()
			title = field_name.upper().replace("ERROR", "ERR").replace("WAVELENGTH", "WAVE")
			if (title + ' COL NUM') in metadata_fields:
				try: column_dict[title] = int(value)
				except ValueError: column_dict[title] = None
			else:
				value_dict[title] = value

		file_list.append((value_dict, column_dict))

	return file_list

