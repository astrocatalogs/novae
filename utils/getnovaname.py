import re

__all__ = ['get_nova_name']

def get_nova_name(string):
	string = string.replace("_", "").replace(" ", "").upper()

	if re.match(r"[A-Z]{4}$", string):
		value = string[0] + "_" + string[1] + string[2:4].lower()
	elif re.match(r"[A-Z]{5}$", string):
		value = string[0:2] + "_" + string[2] + string[3:5].lower()
	elif re.match(r"V\d{3}[A-Z]{3}$", string):
		value = string[0:4] + "_" + string[4] + string[5:7].lower()
	elif re.match(r"V\d{4}[A-Z]{3}$", string):
		value = string[0:5] + "_" + string[5] + string[6:8].lower()
	else:
		return None
	
	if value.endswith('Crb'): value = value[:-1] + 'B'
	if value.endswith('Cra'): value = value[:-1] + 'A'
	return value
