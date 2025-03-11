import random
import string


def get_random_string(length=6):
	# choose from all lowercase letter
	letters = string.ascii_letters + string.digits
	result_str = ''.join(random.choice(letters) for i in range(length))
	return result_str


# print(get_random_string(6))
