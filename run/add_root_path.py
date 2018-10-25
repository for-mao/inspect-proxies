from sys import path
from os.path import dirname
from os.path import abspath


root_path = dirname(dirname(abspath(__file__)))
path.append(root_path)