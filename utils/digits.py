__all__ = ['get_dec_digits']

def get_dec_digits(string):
	
	for i in range(len(string)):
		if string[i] == '.':
			return len(string) - i - 1

	return 0
