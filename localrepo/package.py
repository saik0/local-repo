#!/usr/bin/env python3.2

from os.path import abspath, basename, isfile, isdir, join
from subprocess import call
from hashlib import sha256

import os
import shutil
import tempfile
import tarfile
import re

class Package:

	''' Static package '''

	tmpdir = None

	@staticmethod
	def get_tmpdir():
		if Package.tmpdir is None:
			Package.tmpdir = tempfile.mkdtemp('-local-repo')
		return Package.tmpdir

	@staticmethod
	def clean():
		if Package.tmpdir is not None:
			shutil.rmtree(Package.tmpdir)

	@staticmethod
	def from_remote_tarball(url):
		tmpdir = Package.get_tmpdir()
		tarball = basename(url)
		os.chdir(tmpdir)

		if call(['wget', '-O', tarball, url]) is not 0:
			raise Exception('An error ocurred in wget')

		return Package.from_tarball(join(tmpdir, tarball))

	@staticmethod
	def from_tarball(path):
		tmpdir = Package.get_tmpdir()
		path = abspath(path)

		if not isfile(path) or not tarfile.is_tarfile(path):
			raise Exception('File is no valid tarball: {0}'.format(path))

		os.chdir(tmpdir)
		archive = tarfile.open(path)
		name = None

		for member in archive.getnames():
			if member.startswith('/') or member.startswith('..'):
				raise Exception('Tarball contains bad member: {0}'.format(member))

			root = member.split(os.sep)[0]

			if name is None:
				name = root
				continue

			if name != root:
				raise Exception('Tarball contains multiple root directories')

		archive.extractall()
		os.chdir(join(tmpdir, name))

		if call(['makepkg', '-s']) is not 0:
			raise Exception('An error ocurred in makepkg')

		filename = None

		for f in os.listdir():
			if f.endswith('.pkg.tar.xz'):
				filename = f
				continue

		if filename is None:
			raise Exception('Could not find any package')

		return Package.from_file(join(os.getcwd(), filename))

	@staticmethod
	def from_file(path):
		path = abspath(path)

		''' AAAAARRRGG

		The current version of tarfile (0.9) does not support lzma compressed archives.
		The next version will: http://hg.python.org/cpython/file/default/Lib/tarfile.py '''

		#if not isfile(path) or not tarfile.is_tarfile(path):
		#	raise Exception('File is not a valid package: {0}'.format(path))

		#pkg = tarfile.open(path)

		#try:
		#	pkginfo = pkg.extractfile('.PKGINFO').read().decode('utf8')
		#except:
		#	raise Exception('File is not valid package: {0}'.format(path))

		''' Begin workaround '''
		if not isfile(path):
			raise Exception('File does not exist: {0}'.join(path))

		tmpdir = Package.get_tmpdir()

		if call(['tar', '-xJf', path, '-C', tmpdir, '.PKGINFO']) is not 0:
			raise Exception('An error occurred in tar')

		pkginfo = open(join(tmpdir, '.PKGINFO')).read()
		''' End workaround '''

		info = {'pkgname': None, 'pkgver': None, 'arch': None}

		for i in info:
			m = re.search('{0} = ([^\n]+)\n'.format(i), pkginfo)

			if m is None:
				raise Exception('Invalid .PKGINFO')

			info[i] = m.group(1)

		return Package(info['pkgname'], info['pkgver'], path, {'arch': info['arch']})

	@staticmethod
	def forge(path):
		if path.startswith('http://') or path.startswith('ftp://'):
			return Package.from_remote_tarball(path)

		if path.endswith('.tar.gz'):
			return Package.from_tarball(path)

		if path.endswith('.pkg.tar.xz'):
			return Package.from_file(path)

		raise Exception('Invalid file name: {0}'.format(path))

	''' Package object '''

	def __init__(self, name, version, path, infos=None):
		self._name = name
		self._version = version
		self._filename = basename(path)
		self._path = abspath(path)
		self._infos = infos

	@property
	def name(self):
		return self._name

	@property
	def version(self):
		return self._version

	@property
	def path(self):
		return self._path

	@property
	def infos(self):
		infos = self._infos
		infos['name'] = self._name
		infos['version'] = self._version
		infos['filename'] = self._filename
		return infos

	@property
	def has_valid_sha256sum(self):
		if not 'sha256sum' in self._infos:
			return False

		try:
			f = open(self._path, 'rb')
			if sha256(f.read()).hexdigest() != self._infos['sha256sum']:
				return False
		except:
			return False

		return True

	def move(self, path):
		path = abspath(path)

		if not isdir(path):
			raise Exception('Destination is no directory: {0}'.format(path))

		path = join(path, self._filename)

		if isfile(path):
			raise Exception('File already exists: {0}'.format(path))

		shutil.move(self._path, path)
		self._path = path

	def remove(self):
		if not isfile(self._path):
			raise Exception('Package does not exist: {0}'.format(self._path))

		os.remove(self._path)