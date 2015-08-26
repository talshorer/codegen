#! /usr/bin/python3

if __name__ == "__main__":
    import os
    import sys
    import unittest
    search_path = os.path.join(os.getcwd(), os.path.dirname(__file__))
    sys.path.append(os.path.realpath(os.path.join(search_path, "..")))
    test_suite = unittest.TestLoader().discover(search_path)
    unittest.main(defaultTest="test_suite", verbosity=2)
