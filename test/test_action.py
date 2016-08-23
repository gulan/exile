#!/usr/bin/env python

import os
from os import path
import shutil
import subprocess
import tempfile
import unittest
import exile_utils
import exiler
import sys

class TestAction(unittest.TestCase):

    def setUp(self):
        self.save = os.getcwd()
        self.root = exile_utils.make_testbed()
        self.exile_script = path.abspath('./exiling')
        self.pardon_script = path.abspath('./exiling')
        
    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self.save)
        
    def test_exile(self):
        r = self.root
        ps = exiler.projects(r)
        p = ps[1] # choose a project
        cs = exiler.candidates(r, p)
        c = cs[1] # choose a candidate
        # os.chdir(path.join(r, p)) # exile is run within a project dir

        cmdl = [self.exile_script, 'exile', '-r', self.root, '-p', p, c]
        # print >>sys.stderr, '> %s' % ' '.join(cmdl)
        rc = subprocess.call(cmdl)

        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        fs = exiler.folders(r, p)
        self.assertEqual(c in fs, True)
        self.assertEqual(c not in exiler.candidates(r, p), True)
        self.assertEqual(exile_utils.check(r)[0], True)

    def test_pardon(self):
        r = self.root
        ps = exiler.projects(r)
        p = ps[1] # choose a project
        cs = exiler.candidates(r, p)
        c = cs[1] # choose a candidate

        # os.chdir(path.join(r, p)) # exile is run within a project dir
        cmdl = [self.exile_script, 'exile', '-r', self.root, '-p', p, c]
        rc = subprocess.call(cmdl)
        
        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        self.assertEqual(exile_utils.check(r)[0], True)
        fs = exiler.folders(r, p)
        self.assertEqual(c in fs, True)
        self.assertEqual(c not in exiler.candidates(r, p), True)

        cmdl = [self.exile_script, 'pardon', '-r', self.root, '-p', p, c]
        rc = subprocess.call(cmdl) # undo exile
        self.assertEqual(rc, 0)

        # print "project>", p
        # subprocess.call(['tree', exiler.dot_exile(r)])
        ck = exile_utils.check(r)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exiler.folders(r, p)
        self.assertEqual(c not in fs, True)
        self.assertEqual(c in exiler.candidates(r, p), True)

if __name__ == '__main__':
    unittest.main()


    
