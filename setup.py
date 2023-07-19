from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

#with open("README.md", 'r') as f:
#    long_description = f.read()

setup(
    name='dst_evidence_combinator',
    version='0.1',
    description='DST-based toxicological evidence combinator',
    license='GNU',
#    long_description=long_description,
    author='Karolina Kopanska',
    author_email='karolinaweronika.kopanska@upf.edu',
    url='https://github.com/phi-grib/dst_evidence_combinator',
    download_url='https://github.com/phi-grib/dst_evidence_combinator.git',
    packages=find_packages(),
    # If any package contains *.txt or *.rst files, include them:
    # package_data={'': ['*.yaml', '*.yml']},
    package_data={'combine': ['config.yaml']}
)