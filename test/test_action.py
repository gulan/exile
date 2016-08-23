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
        try:
            del os.environ['EXILER_ROOT']
        except KeyError:
            pass
        self.root = exile_utils.make_testbed()
        self.exile_script = path.abspath('./occ')
        self.pardon_script = path.abspath('./occ')
        ps = exile.projects(self.root)
        self.project = ps[1] # choose an arbitrary project
        cs = exile.candidates(self.root, self.project)
        self.cand = cs[1] # choose an arbitrary subdirectory of the project
        
    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self.save)
        
    def test_exile(self):
        cmdl = [self.exile_script, 'exile', '-r', self.root, '-p', self.project, self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand in fs)
        self.assertTrue(self.cand not in exile.candidates(self.root, self.project))
        self.assertTrue(exile_utils.check(self.root)[0])

    def test_pardon(self):
        cmdl = [self.exile_script, 'exile', '-r', self.root, '-p', self.project, self.cand]
        rc = subprocess.call(cmdl)
        
        self.assertEqual(rc, 0)
        # verify the candidate subdir is now exiled:
        self.assertTrue(exile_utils.check(self.root)[0])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand in fs)
        self.assertTrue(self.cand not in exile.candidates(self.root, self.project))
        
        cmdl = [self.exile_script, 'pardon', '-r', self.root, '-p', self.project, self.cand]
        rc = subprocess.call(cmdl) # undo exile
        self.assertEqual(rc, 0)
        
        # subprocess.call(['tree', exile.dot_exile(self.root)])
        ck = exile_utils.check(self.root)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand not in fs)
        self.assertTrue(self.cand in exile.candidates(self.root, self.project))

    def test_pardon_implict_root(self):
        os.environ['EXILER_ROOT'] = self.root
        cmdl = [self.exile_script, 'exile', '-p', self.project, self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        self.assertTrue(exile_utils.check(self.root)[0])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand in fs)
        self.assertTrue(self.cand not in exile.candidates(self.root, self.project))
        cmdl = [self.exile_script, 'pardon', '-p', self.project, self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        ck = exile_utils.check(self.root)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand not in fs)
        self.assertTrue(self.cand in exile.candidates(self.root, self.project))
        
    def test_exile_no_root(self):
        # expect error
        cmdl = [self.exile_script, 'exile', '-p', self.project, self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 9)
        self.assertTrue(exile_utils.check(self.root)[0])
        
    def test_pardon_implict_project(self):
        os.chdir(path.join(self.root, self.project)) # exile is run within a project dir
        cmdl = [self.exile_script, 'exile', '-r', self.root, self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        self.assertTrue(exile_utils.check(self.root)[0])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand in fs)
        self.assertTrue(self.cand not in exile.candidates(self.root, self.project))
        cmdl = [self.exile_script, 'pardon', '-r', self.root, self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        ck = exile_utils.check(self.root)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand not in fs)
        self.assertTrue(self.cand in exile.candidates(self.root, self.project))

    def test_pardon_implict_root_and_project(self):
        # the most common case
        os.environ['EXILER_ROOT'] = self.root
        os.chdir(path.join(self.root, self.project))
        cmdl = [self.exile_script, 'exile', self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        self.assertTrue(exile_utils.check(self.root)[0])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand in fs)
        self.assertTrue(self.cand not in exile.candidates(self.root, self.project))
        cmdl = [self.exile_script, 'pardon', self.cand]
        rc = subprocess.call(cmdl)
        self.assertEqual(rc, 0)
        ck = exile_utils.check(self.root)
        self.assertEqual(ck, (True, ''), ck[1])
        fs = exile.folders(self.root, self.project)
        self.assertTrue(self.cand not in fs)
        self.assertTrue(self.cand in exile.candidates(self.root, self.project))

if __name__ == '__main__':
    unittest.main()


    
