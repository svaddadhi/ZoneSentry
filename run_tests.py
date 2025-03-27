import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    test_suite.addTests(test_loader.discover(test_dir, pattern='test_*.py'))
    
    return test_suite

if __name__ == '__main__':
    test_suite = create_test_suite()
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful())