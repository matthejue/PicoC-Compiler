#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os

print(os.path.dirname(sys.argv[0]))


directory_path = os.getcwd()
print("My current directory is : " + directory_path)
folder_name = os.path.basename(directory_path)
print("My directory name is : " + folder_name)
