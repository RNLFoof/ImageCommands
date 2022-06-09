from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='ImageCommands',
   version='1.0',
   description='Beware',
   license="MIT",
   long_description=long_description,
   author='Zachary Zablotsky',
   url="https://github.com/RNLFoof/ImageCommands",
   packages=['ZachsStupidImageLibrary'],
   install_requires=['Pillow', 'wand']
)