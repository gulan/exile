#!/usr/bin/env python

import exile
import exile_utils
import os
from os import path
import shutil
import subprocess
import sys
import tempfile
import unittest

class TestAction(unittest.TestCase):

    def setUp(self):
        self.save = os.getcwd()
        self.root = exile_utils.make_testbed()
        self.exile_script = path.abspath('./occ')
        self.pardon_script = path.abspath('./occ')
        
    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self.save)
        
    def test_exile(self):
        r = self.root
        ps = exile.projects(r)
        p = ps[1] # choose a project
        cs = exile.candidates(r, p)
        c = cs[1] # choose a candidate
        # os.chdir(path.join(r, p)) # exile is run within a project dir

        cmdl = [self.exile_script, 'exile', '-r', self.root, '-p', p, c]
        # print >>sys.stderr, '> %s' % ' '.join(cmdl)
        rc = subprocess.call(cmdl)

        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        fs = exile.folders(r, p)
        self.assertEqual(c in fs, True)
        self.assertEqual(c not in exile.candidates(r, p), True)
        self.assertEqual(exile_utils.check(r)[0], True)

    def test_pardon(self):
        r = self.root
        ps = exile.projects(r)
        p = ps[1] # choose a project
        cs = exile.candidates(r, p)
        c = cs[1] # choose a candidate

        # os.chdir(path.join(r, p)) # exile is run within a project dir
        cmdl = [self.exile_script, 'exile', '-r', self.root, '-p', p, c]
        rc = subprocess.call(cmdl)
        
        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        self.assertEqual(exile_utils.check(r)[0], True)
        fs = exile.folders(r, p)
        self.assertEqual(c in fs, True)
        self.assertEqual(c not in exile.candidates(r, p), True)

        cmdl = [self.exile_script, 'pardon', '-r', self.root, '-p', p, c]
        rc = subprocess.call(cmdl) # undo exile
        self.assertEqual(rc, 0)

        # print "project>", p
        # subprocess.call(['tree', exile.dot_exile(r)])
        ck = exile_utils.check(r)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exile.folders(r, p)
        self.assertEqual(c not in fs, True)
        self.assertEqual(c in exile.candidates(r, p), True)

if __name__ == '__main__':
    unittest.main()


    
