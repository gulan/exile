#!/usr/bin/env python

import os
import shutil
import sys
import tempfile

"""
The structure of a projects directory has three levels of interst to us. 

  * a single root directory
  * any number of project directories
  * any number of items with a project directory

The items may be files or directories, but their exact structure and
content do not concern us. I just declare that an item contains one or
more filetrees.

    root = project*
    project = item*
    item = file | subdir
    subdir = filetree*

The exile program is run when the cwd is one of the projects. We
require a .exile directory as a sibling to the project directories. A
better structure is

    root = dot_exile . projects
    projects = project*
    project = item*
    item = file | subdir
    subdir = filetree*
    dot_exile = archived*
    archived = folder*
    folder = filetree*

The dot_exile directory has any number of 'archived' directories. The
archives names are a subset of the project names. (The dot_exile is
meant to partially parallel the root directory.)

The folder within a archived directory were once subdirs of the project. 

"""

class Check(Exception): pass

def make_testbed(with_exile=True):
    
    def populate(sd):
        for _ in range(2):
            _, p = tempfile.mkstemp(prefix='x_', dir=sd)
            yield p
            
    root = tempfile.mkdtemp(prefix='exile_root_')
    if with_exile:
        os.mkdir(os.path.join(root, '.exile'))
    projects = []
    p_contents = []
    for i in range(5):
        d = tempfile.mkdtemp(prefix='proj_', dir=root)
        projects.append(d)
        subdirs = []
        for j in range(3):
            e = tempfile.mkdtemp(prefix='sub_', dir=d)
            subdirs.append(e)
            list(populate(e))
    p_contents.append(subdirs)
    return root

def check_consistent(root):
    """Verify all projects are consistent with the exile
    archive. Every exile and pardon command should preserve the
    invariants checked here."""

    if os.path.islink(root) or not os.path.isdir(root):
        raise Check("projects root %s is not a directory" % root)

    dot_exile = os.path.join(root, '.exile')
    if not os.path.lexists(dot_exile):
        raise Check("projects root %s has no .exile" % root)
    if os.path.islink(dot_exile) or not os.path.isdir(dot_exile):
        raise Check(".exile in projects root %s is not a directory" % root)

    def check_link_target(project_name, folder_name):
        target = os.path.join(dot_exile, project_name, folder_name)
        if not os.path.lexists(target):
            raise Check("archived folder %s does not exist" % target)
        if os.path.islink(target):
            raise Check("archived folder %s is itself a symlink" % target)
        if not os.path.isdir(target):
            raise Check("archived folder %s is not a directory" % target)
    
    def check_link_source(project_name, folder_name):
        target = os.path.join(dot_exile, project_name, folder_name)
        source = os.path.join(root, project_name, folder_name)
        if not os.path.islink(source):
            raise Check("source %s is not a symlink" % source)
        if os.readlink(source) != target:
            msg = "source %s does not point to target %s"
            raise Check(msg % (source, target))
    
    for project_name in os.listdir(dot_exile):
        full_archived_project_path = os.path.join(dot_exile, project_name)
        folders = os.listdir(full_archived_project_path)
        if not folders:
            msg = ".exile project directory %s has no folders"
            raise Check(msg % full_archived_project_path)
        for folder_name in folders:
            check_link_target(project_name, folder_name)
            check_link_source(project_name, folder_name)


def check(root):
    'functional wrapper'
    try:
        check_consistent(root)
        return (True, '')
    except Check, msg:
        return (False, msg)

# The functions below assume that check(root) is true.

def projects(root):
    return [p for p in os.listdir(root) if p != '.exile']

def dot_exile(root):
    return os.path.join(root, '.exile')

def shadows(root, fullpath=False):
    """A shadow directory has the same name as a project
    directory. The shadow directory exists only if the original
    project directory as exiled some directories."""
    def aux():
        for f in os.listdir(dot_exile(root)):
            if fullpath:
                yield os.path.join(dot_exile(root), f)
            else:
                yield f
    return list(aux())

def folders(root, project, fullpath=False):
    """The exiled target directories for this project"""
    def aux():
        loc = os.path.join(dot_exile(root), project)
        # A project may have nothing exiled
        if os.path.exists(loc):
            for f in os.listdir(loc):
                if fullpath:
                    yield os.path.join(dot_exile(root), project, f)
                else:
                    yield f
    return list(aux())

def candidates(root, project, fullpath=False):
    """Return a list of a project's subdirectories. Any of these could
    be made an exile."""
    def aux():
        for p in os.listdir(os.path.join(root, project)):
            fp = os.path.join(root, project, p)
            if os.path.islink(fp):
                continue
            if not os.path.isdir(fp):
                continue
            if fullpath:
                yield fp
            else:
                yield p
    return list(aux())

"""
exile_utils.py make
root=/tmp/exile_root_Wq7FhO
exile_utils.py check $root
exile_utils.py dot $root
exile_utils.py projects $root
exile_utils.py shadows $root
exile_utils.py candidates $root proj_DvzXTM
exile_utils.py folders $root proj_DvzXTM
tree $root/proj_DvzXTM
tree $root/.exile/proj_DvzXTM
"""

if __name__ == '__main__':
    if 'make' in sys.argv:
        print make_testbed()
        sys.exit(0)
    elif 'check' in sys.argv:
        root = sys.argv[sys.argv.index('check') + 1]
        try:
            check_consistent(root)
        except Check, msg:
            # print >>sys.stderr, msg
            raise 
            sys.exit(1)
    elif 'dot' in sys.argv:
        root = sys.argv[sys.argv.index('dot') + 1]
        print dot_exile(root)
        sys.exit(0)
    elif 'projects' in sys.argv:
        root = sys.argv[sys.argv.index('projects') + 1]
        for p in projects(root):
            print p
        sys.exit(0)
    elif 'shadows' in sys.argv:
        root = sys.argv[sys.argv.index('shadows') + 1]
        try:
            option = (sys.argv[sys.argv.index('shadows') + 2] == '-l')
        except IndexError:
            option = False
        for s in shadows(root, option):
            print s
        sys.exit(0)
    elif 'folders' in sys.argv:
        root = sys.argv[sys.argv.index('folders') + 1]
        project = sys.argv[sys.argv.index('folders') + 2]
        try:
            option = (sys.argv[sys.argv.index('folders') + 3] == '-l')
        except IndexError:
            option = False
        for s in folders(root, project, option):
            print s
        sys.exit(0)
    elif 'candidates' in sys.argv:
        root = sys.argv[sys.argv.index('candidates') + 1]
        project = sys.argv[sys.argv.index('candidates') + 2]
        try:
            option = (sys.argv[sys.argv.index('candidates') + 3] == '-l')
        except IndexError:
            option = False
        for s in candidates(root, project, option):
            print s
        sys.exit(0)
    else:
        print >>sys.stderr, "no args"
        sys.exit(2)
        


    
