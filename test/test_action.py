#!/usr/bin/env python

import os
import shutil
import subprocess
import tempfile
import unittest
import exile_utils

"""
exile -h
exile proj
"""

class TestAction(unittest.TestCase):

    def setUp(self):
        self.save = os.getcwd()
        self.root = exile_utils.make_testbed()
        self.exile_script = os.path.abspath('./exile')
        self.pardon_script = os.path.abspath('./pardon')
        
    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self.save)
        
    def test_exile(self):
        r = self.root
        ps = exile_utils.projects(r)
        p = ps[1] # choose a project
        cs = exile_utils.candidates(r, p)
        c = cs[1] # choose a candidate
        os.chdir(os.path.join(r, p)) # exile is run within a project dir
        rc = subprocess.call([self.exile_script, c])
        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        fs = exile_utils.folders(r, p)
        self.assertEqual(c in fs, True)
        self.assertEqual(c not in exile_utils.candidates(r, p), True)
        self.assertEqual(exile_utils.check(r)[0], True)

    def test_pardon(self):
        r = self.root
        ps = exile_utils.projects(r)
        p = ps[1] # choose a project
        cs = exile_utils.candidates(r, p)
        c = cs[1] # choose a candidate

        os.chdir(os.path.join(r, p)) # exile is run within a project dir
        rc = subprocess.call([self.exile_script, c])
        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        self.assertEqual(exile_utils.check(r)[0], True)
        fs = exile_utils.folders(r, p)
        self.assertEqual(c in fs, True)
        self.assertEqual(c not in exile_utils.candidates(r, p), True)

        rc = subprocess.call([self.pardon_script, c]) # undo exile
        self.assertEqual(rc, 0)
        # print "project>", p
        # subprocess.call(['tree', exile_utils.dot_exile(r)])
        ck = exile_utils.check(r)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exile_utils.folders(r, p)
        self.assertEqual(c not in fs, True)
        self.assertEqual(c in exile_utils.candidates(r, p), True)

if __name__ == '__main__':
    unittest.main()


    
