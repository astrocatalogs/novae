from ..nova import NOVA
from astrocats.catalog.utils import pbar
import os
import os.path
from ..utils import read_photometry_ticket, get_nova_name, convert_date_UTC
import re
import csv
from astropy.time import Time


def do_photometry(catalog):
	"""
	"""
	#path to root ONC directory
	ONC = catalog.get_current_task_repo()
	ticket_directory = os.path.join(ONC, 'Tickets', 'CompletedTickets')
	task_str = catalog.get_current_task_str()
	
	for filename in pbar(os.listdir(ticket_directory), task_str):
		raw_dict, column_dict = {}, {}		
		
		if not re.search(r'photometry', filename.lower()):
			continue
		with open(os.path.join(ticket_directory, filename)) as phot_ticket:
			try:			
				raw_dict, column_dict = read_photometry_ticket(phot_ticket.read())
				phot_ticket.close()
			except:
				True == True
				#print(filename)
				continue
				#THROW ERROR TO LOG HERE
		
		if raw_dict['REFERENCE'] == 'AAVSO': continue

		nova_name = get_nova_name(raw_dict['OBJECT NAME'])
		filename = raw_dict['DATA FILENAME']
		file_path = os.path.join(ONC, "Individual_Novae", nova_name, "Data", filename)
	
		name = nova_name.replace('_', ' ')
		name = catalog.add_entry(name)
	
		if type(raw_dict['BIBCODE']) is str and len(raw_dict['BIBCODE']) == 19:
			source = catalog.entries[name].add_source(bibcode=raw_dict['BIBCODE'], reference=raw_dict['REFERENCE'])
		else:
			source = catalog.entries[name].add_source(bibcode='1234567890123456789', reference=raw_dict['REFERENCE'])
		catalog.entries[name].add_quantity(NOVA.ALIAS, name, source)
		
		csvfile = open(file_path)
		contents = list(csv.reader(csvfile, delimiter=',', quotechar='"'))
		
		
		
		time_offset = 0
		if re.match(r'dpo', raw_dict['TIME UNITS'].lower()):
			t = Time(convert_date_UTC(raw_dict['ASSUMED DATE OF OUTBURST']))
			offset = t.jd 

		column_corr = {'TIME': 'time', 'FILTER/FREQUENCY/ENERGY RANGE': 'band', 'TELESCOPE': 'telescope', 'OBSERVER': 'observer', 'FILTER SYSTEM': None, 'UPPER LIMIT FLAG': None}

		if re.search(r'mag', raw_dict['FLUX UNITS'].lower()): column_corr['FLUX'] = 'magnitude'
		else: column_corr['FLUX'] = 'flux'

		if re.search(r'mag', raw_dict['FLUX ERROR UNITS'].lower()): column_corr['FLUX ERROR'] = 'e_magnitude'
		else: column_corr['FLUX ERROR'] = 'e_flux'

		for line in pbar(contents, name):
			data_dict = {}
			line = [value.strip() for value in line]
			if line[0].startswith("#"): continue
				
			for key in column_dict:
				if column_dict[key] is None or line[column_dict[key]] == '':
					continue
				data_dict[column_corr[key]] = line[column_dict[key]]
				
			#if re.match(r'ut', raw_dict['TIME UNITS'].lower()):
			#	data_dict['time'] = (Time(data_dict)).jd
			#data_dict['time'] += offset
			if None in data_dict: del data_dict[None]
			
			
			if 'telescope' not in data_dict: data_dict['telescope'] = raw_dict['TELESCOPE']
			if 'observer' not in data_dict: data_dict['observer'] = raw_dict['OBSERVER']
			data_dict['u_time'] = 'MJD'
			key_list = list(data_dict.keys())
			for key in key_list:
				if data_dict[key] is None:
					del data_dict[key]
			
			if data_dict['time'] >= 2400000:
				data_dict['time'] -= 2400000
			
			data_dict['source'] = source
			
			catalog.entries[name].add_photometry(**data_dict)
		csvfile.close()
		catalog.journal_entries()
		
	return
			
