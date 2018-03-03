#! /usr/bin/python
# utest.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# Runs specified Archy unit test.
# If no parameters is specified runs all unit tests in "utest" package -
# tests found under "utest" directory and subdirectories.
# Unit test file is considered a .py file which has name ending on "Test"
# (case is important)

import utest.run_tests

utest.run_tests.run()

