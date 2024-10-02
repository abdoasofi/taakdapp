from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in taakd_new/__init__.py
from taakd_new import __version__ as version

setup(
	name='taakd_new',
	version=version,
	description='customize in erpnext',
	author='Taakd',
	author_email='abdoalsofi576@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
