from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


setup(
    name='TOXTRUST',
    version='0.2',
    description='DST-based toxicological evidence combinator',
    license='GNU',
#    long_description=long_description,
    author='Karolina Kopanska',
    author_email='karolinaweronika.kopanska@upf.edu',
    url='https://github.com/phi-grib/TOXTRUST',
    download_url='https://github.com/phi-grib/TOXTRUST.git',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['toxtrust=toxtrust.console:main'],
    },
    # If any package contains *.txt or *.rst files, include them:
    # package_data={'': ['*.yaml', '*.yml']},
    package_data={'toxtrust': ['config.yaml']}
)
