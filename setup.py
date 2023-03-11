from os import path
from subprocess import SubprocessError, check_output

from setuptools import setup

with open('./requirements.txt') as f:
    required = f.read().splitlines()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version = '1.0.0'

try:
    version = (
        check_output(['git', 'describe', '--tags']).strip().decode().replace('v', '')
    )
except SubprocessError as e:
    print(e)

setup(
    name='readwise',
    version=version,
    description='Readwise api client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='rwxd',
    author_email='rwxd@pm.me',
    url='https://github.com/rwxd/pyreadwise',
    license='MIT',
    packages=['readwise'],
    install_requires=required,
    classifiers=[
        'Programming Language :: Python :: 3.11',
    ],
)
