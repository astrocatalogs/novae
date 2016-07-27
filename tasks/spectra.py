from ..nova import NOVA
from astrocats.catalog.utils import pbar
import os
import os.path
from ..utils import read_spectra_ticket, read_spectra_metadata, get_nova_name, convert_date_UTC, get_dec_digits
import re
import csv
from astropy.time import Time

def do_spectra(catalog):
	"""		
	"""

	#path to root ONC directory
	ONC = catalog.get_current_task_repo()
	novae_directory = os.path.join(ONC, 'Individual_Novae')
	task_str = catalog.get_current_task_str()

	for indiv_nova in pbar(os.listdir(novae_directory), task_str):
		nova_dir = os.path.join(novae_directory, indiv_nova)
		indiv_nova = get_nova_name(indiv_nova)

		if not os.path.isdir(nova_dir) or indiv_nova is None: continue

		ticket_directory = os.path.join(nova_dir, "Tickets", "CompletedTickets")
		for ticket in os.listdir(ticket_directory):
			ticket_raw_dict, ticket_column_dict = {}, {}			
			if not re.search(r'spectra', ticket.lower()): continue

			with open(os.path.join(ticket_directory, ticket)) as spec_ticket:
				try:
					ticket_raw_dict, ticket_column_dict = read_spectra_ticket(spec_ticket.read())
					spec_ticket.close()
				except AttributeError:
					True == True
					print(ticket)
					continue
					#THROW ERROR TO LOG HERE

			meta_filename = ticket_raw_dict['METADATA FILENAME']
			file_path = os.path.join(nova_dir, "Data", meta_filename)
			
			name = indiv_nova.replace('_', ' ')
			name = catalog.add_entry(name)
			if type(ticket_raw_dict['BIBCODE']) is str and len(ticket_raw_dict['BIBCODE']) == 19:
				source = catalog.entries[name].add_source(bibcode=ticket_raw_dict['BIBCODE'], reference=ticket_raw_dict['REFERENCE'])
			else:
				source = catalog.entries[name].add_source(bibcode='couldnotfindbibcode', reference=ticket_raw_dict['REFERENCE'])
			catalog.entries[name].add_quantity(NOVA.ALIAS, name, source)
			

			time_offset = 0		
			if re.match(r'(days)|(ut)', ticket_raw_dict['TIME SYSTEM'].lower()):
				t = Time(convert_date_UTC(ticket_raw_dict['ASSUMED DATE OF OUTBURST']))
				offset = t.jd 
			
			mag = 'magnitude' if re.search(r'mag', ticket_raw_dict['FLUX UNITS'].lower()) else 'flux'
			e_mag = 'e_magnitude' if re.search(r'mag', ticket_raw_dict['FLUX ERROR UNITS'].lower()) else 'e_flux'
				
			with open(file_path, "r") as metadata_file:
				data_file_list = read_spectra_metadata(metadata_file.read(), ticket_column_dict)
				metadata_file.close()
 
			for metadata_raw_dict, metadata_column_dict in data_file_list:				
				data_filename = metadata_raw_dict['FILENAME']
				csvfile = open(os.path.join(nova_dir, "Data", data_filename))
				contents = list(csv.reader(csvfile, delimiter=',', quotechar='"'))
				csvfile.close()

				flux_col = metadata_column_dict['FLUX']
				wavelength_col = metadata_column_dict['WAVE']
				flux_err_col = metadata_column_dict['FLUX ERR']
				
				if flux_col is None or wavelength_col is None: continue
				
				flux_err_arr = None if flux_err_col is None else []
				flux_arr, wavelength_arr = [],[]

				for line in contents:
					line = [value.strip() for value in line]
					if line[0].startswith("#"): continue
					
					try:
						flux = line[flux_col]
						wavelength = line[wavelength_col]
					except (IndexError, ValueError):
						continue
					try: flux_err = None if flux_err_arr is None else line[flux_err_col]
					except (IndexError, ValueError): flux_err = None
					
					if flux_err is not None: flux_err_arr.append(flux_err)
					flux_arr.append(flux)
					wavelength_arr.append(wavelength)
		
				data_dict = {'wavelengths': wavelength_arr, 'fluxes': flux_arr, 'source': source, 'time': metadata_raw_dict['DATE'], 'observer': metadata_raw_dict['OBSERVER'], 'telescope': metadata_raw_dict['TELESCOPE'], 'instrument': metadata_raw_dict['INSTRUMENT'], 'u_wavelengths': 'Angstrom', 'u_time': 'MJD', 'u_fluxes': 'erg/s/cm^2'}

				if not flux_err_arr is None and len(flux_err_arr) != len(wavelength_arr):
					data_dict['errors'] = flux_err_arr

				if float(data_dict['time']) >= 2400000:
					str(get_dec_digits(data_dict['time']))
					data_dict['time'] == ("{:.%sf}" %(str(get_dec_digits(data_dict['time'])))).format(float(data_dict['time']) - 2400000)

				key_list = list(data_dict.keys())
				for key in key_list:
					if data_dict[key] is None:
						del data_dict[key]

				
				catalog.entries[name].add_spectrum(**data_dict)
			catalog.journal_entries()	

	return

