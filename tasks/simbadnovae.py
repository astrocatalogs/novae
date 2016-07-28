from ..nova import NOVA
import re
from astroquery.simbad import Simbad
from astrocats.catalog.utils import pbar, tprint
from ..utils import get_nova_name


def do_simbad_novae(catalog):
	task_str = catalog.get_current_task_str()	
	simbad_mirrors = ['http://simbad.harvard.edu/simbad/sim-script',
                     'http://simbad.u-strasbg.fr/simbad/sim-script']

	for mirror in simbad_mirrors:
        customSimbad.SIMBAD_URL = mirror
        try:
            table = customSimbad.query_criteria('maintype=No* | maintype="No?"')
        except:
            continue
        else:
            break

    if not table:
        catalog.log.warning('SIMBAD unable to load, probably offline.')

	
	customSimbad = Simbad()
	customSimbad.ROW_LIMIT = -1
	customSimbad.TIMEOUT = 120

	for name in pbar(catalog.entries, task_str):
		try:
			nova_name = "V* " + get_nova_name(name)
			aliases = customSimbad.query_objectids(nova_name)
		except:
			#THROW WARNING HERE
			tprint("Could not find " + nova_name)
			continue
		
		table = customSimbad.query_object(nova_name)
		
		name = catalog.add_entry(name)
		
		bibcode = table[0]['COO_BIBCODE'].decode()
		ra = str(table[0]['RA'])
		dec = str(table[0]['DEC'])
		
		source = catalog.entries[name].add_source(name='SIMBAD astronomical database',
													bibcode=bibcode,
													url="http://simbad.u-strasbg.fr/",
                              						secondary=True)
		catalog.entries[name].add_quantity(NOVA.RA, ra, source)
		catalog.entries[name].add_quantity(NOVA.DEC, dec, source)

		for i in range(len(aliases)):
			try: alias = aliases[i][0].decode()
			except:	alias = str(aliases[i][0])
						
			catalog.entries[name].add_quantity(NOVA.ALIAS, alias, source)
		
		catalog.journal_entries()
			
