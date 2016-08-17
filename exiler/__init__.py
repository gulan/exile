from collections import namedtuple
import os
from os import path
import shutil
import sys

Status = namedtuple("Status", "status rc msg")

def trim(name):
    if name.startswith('./'): 
        name = name[2:]
    if name.endswith('/'):
        name = name[:-1]
    return name

def projects(root):
    return [p for p in os.listdir(root) if p != '.exile']

def dot_exile(root):
    return path.join(root, '.exile')

def shadows(root, fullpath=False):
    """A shadow directory has the same name as a project
    directory. The shadow directory exists only if the original
    project directory as exiled some directories."""
    def aux():
        for f in os.listdir(dot_exile(root)):
            (yield path.join(dot_exile(root), f)) if fullpath else (yield f)
    return list(aux())

def folders(root, project, fullpath=False):
    """The exiled target directories for this project"""
    def aux():
        loc = path.join(dot_exile(root), project)
        # A project may have nothing exiled
        if path.exists(loc):
            for f in os.listdir(loc):
                (yield path.join(dot_exile(root), project, f)) if fullpath else (yield f)
    return list(aux())

def candidates(root, project, fullpath=False):
    """Return a list of a project's subdirectories. Any of these could
    be made an exile."""
    def aux():
        for p in os.listdir(path.join(root, project)):
            fp = path.join(root, project, p)
            if path.islink(fp):
                continue
            if not path.isdir(fp):
                continue
            (yield fp) if fullpath else (yield p)
    return list(aux())

def exile(args):
    """
    * check args.source is a local directory
    * find ancestor directory .exile
    * resolve args.source's parent dir to a simple name
    * ensure that the dir .exile/$dir exists
    * move args.source to .exile/$dir/
    * symlink .exile/$dir/args.source to args.source
    """
    source = trim(args.source)

    def check_source(spath):
        if path.sep in spath:
            return Status(False, 19, 'source must be a local directory')
        if not path.exists(spath):
            return Status(False, 18, 'source not found')
        if path.islink(spath):
            return Status(False, 17, 'source may not be a symbolic link')
        if not path.isdir(spath):
            return Status(False, 16, 'source must be a local directory')
        return Status(True, 0, '')

    check = check_source(source)
    if not check.status:
        print >>sys.stderr, check.msg
        return check.rc

    def find_exile():
        spath = os.getcwd()
        while spath != '/': # search towards fs root
            location = path.join(spath, '.exile')
            if path.exists(location):
                return Status(True, 0, location) # found
            spath = path.dirname(spath)
        return Status(False, 49, 'no .exile/ directory found')

    find_result = find_exile()
    if find_result.status:
        exile_path = find_result.msg
    else:
        print >>sys.stderr, find_result.msg
        return find_result.rc

    parent_name = path.basename(os.getcwd())
    new_home = path.join(exile_path, parent_name)
    if not path.exists(new_home):
        os.mkdir(new_home)
    target = path.join(new_home, source)

    shutil.move(source, target)
    os.symlink(target, source)

    return 0

def pardon(args):
    "Restore the exiled directory."
    # pre-conditions:
    # * linkname is a basename
    # * linkname is a symlink in the current directory
    # * linkname really point to a directory in the proper exile directory
    # * user has permissions move all files in the exiled directory
    linkname = trim(args.linkname)

    def check_linkname(linkname):
        if not path.exists(linkname):
            return Status(False, 37, 'real directory not found')
        if not path.islink(linkname):
            return Status(False, 38 ,'linkname must be a symbolic link')
        data = trim(os.readlink(linkname))
        if linkname != path.basename(data):
            msg = 'linkname is not the basename form of the exiled directory'
            return Status(False, 39, msg)
        return Status(True, 0, '')

    check = check_linkname(linkname)
    if not check.status:
        print >>sys.stderr, check.msg
        return check.rc
        
    exiled_folder_path = trim(os.readlink(linkname))
    
    os.remove(linkname)
    shutil.move(exiled_folder_path, linkname)

    # remove exiled project folder if empty
    project_path = path.dirname(exiled_folder_path)
    dot_exile = path.dirname(project_path)
    assert path.basename(dot_exile) == '.exile', ("path error: %r" % dot_exile)
    if os.listdir(project_path) == []:
        os.rmdir(project_path)
        
    return 0

