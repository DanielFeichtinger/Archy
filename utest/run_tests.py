# run_tests.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# Runs specified Archy unit tests or all tests under "utest" directory.
import os
from os.path import join, getsize
import sys
import unittest

EXT = '.py'

def suite(moduleNames):
    alltests = unittest.TestSuite()

    for module in map(get_module, moduleNames):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

# Returns module specified by name
def get_module(name):
    module = __import__(name)
    components = name.split('.')
    for component in components[1:]:
        module = getattr(module, component)
    return module

# Returns true if specified file name confirms to the test module naming conventions
def is_test(file_name): return file_name.endswith('Test' + EXT)

# Returns full name of module. Parameters - package name and module file name
def file_to_module(package, file_name):
    if (package):
        return package + '.' + file_name[:-len(EXT)]
    else:
        return file_name[:-len(EXT)]

# Returns list of all test modules in package utest and subpackages
def get_all_modules():
    modules = []
    for root, dirs, files in os.walk('utest'):
        files = filter(is_test, files)
        package = root.replace(os.sep, '.')
        def to_module(file_name): return file_to_module(package, file_name)
        modules = modules + map(to_module, files)
    return modules

def run():
    if (len(sys.argv) > 1):
        modules = sys.argv[1:]
    else:
        modules = get_all_modules()
    unittest.TextTestRunner().run(suite(modules))

