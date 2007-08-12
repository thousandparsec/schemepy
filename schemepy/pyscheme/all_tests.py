#!/usr/bin/env python
"""Harness to run a bunch of tests."""
import unittest

def suite():
    moduleNames = ['pair',
                   'parser',
                   'pogo',
                   'test_scheme',
                   'test_analyzer',
                   'expressions',
                   'expander',
                   ]

    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for n in moduleNames:
        testCase = loader.loadTestsFromModule(__import__(n))
        suite.addTest(testCase)
    return suite


if __name__ == '__main__':
    suite = suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
