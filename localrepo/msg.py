#!/usr/bin/env python3.2

import re
import sys
import time

class Msg:
	''' A simple class with some static methods for fancy colored output '''

	@staticmethod
	def process(*args):
		''' Prints yellow bold process messages '''
		print('\033[1;33m::', ' '.join(args), '\033[0m')

	@staticmethod
	def error(*args):
		''' Prints red bold error messages '''
		print('\033[1;31m', ' '.join(args), '\033[0m', file=sys.stderr);

	@staticmethod
	def result(*args):
		''' Prints blue bold result messages '''
		print(' \033[1;34m', ' '.join(args), '\033[0m')

	@staticmethod
	def info(*args):
		''' Prints info messages '''
		print('', ' '.join(args))

	@staticmethod
	def yes(*args):
		''' Performs a simple yes/no question '''
		a = input(' ' + ' '.join(args) + '? [y|N] ')
		return False if re.match('^y(?:es)?', a, flags=re.IGNORECASE) is None else True

	@staticmethod
	def is_int(i):
		''' Test a string for integer '''
		try:
			int(i)
			return True
		except:
			return False

	@staticmethod
	def human_fsize(s):
		''' Turns a filesize in bytes into a human readable format '''
		for unit in ['bytes', 'KiB', 'MiB', 'GiB']:
			if s < 1024:
				return '{0} {1}'.format(s, unit)
			s = round((s / 1024), 2)
		return '{0} {1}'.format(s, 'TiB')

	@staticmethod
	def human_date(t):
		''' Converts a unix timestamp into a human readable format '''
		return time.strftime('%a %d %b %Y %H:%M:%S %Z', time.gmtime(t))

	@staticmethod
	def human_infos(infos):
		''' Turns a dict into a human readable info string '''
		trans = {'md5sum': 'MD5sum',
		         'sha256sum': 'SHA256sum',
		         'csize': 'Package size',
		         'isize': 'Installed size'}

		ret = []

		for k, v in infos.items():
			if 'size' in k and Msg.is_int(v):
				v = Msg.human_fsize(int(v))
			elif 'date' in k and Msg.is_int(v):
				v = Msg.human_date(int(v))

			if k in trans:
				k = trans[k]

			ret.append('{0:15}: {1}'.format(k.capitalize(), v))

		return '\n '.join(ret)
