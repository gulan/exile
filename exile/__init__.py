import argparse
import os
from os import path
import shutil
import sys

"""
root = dot_exile . source_project-rep
dot_exile = target_project*
target_project = 

The projects root (1/) is named root. Within root is a '.exile/' and
any number of source_projects. The source projects can be arbitrary
file trees, but some project will have direct subdirectories that are
suitable for exile. If such a subdirectory is exported, we call that
entry the source. Once exiled the source directory will replaced by a
symlink that points to the relocated original source directory.

The root/.exile/ contains any number of target_project
directories. These entries are a subset of the source projects
described above. Inside a target project directory is one or more
target directories. A target diectory is the relocated source
directory as desribed above.

A target project directory is never empty: it is removed when its last
target is removed.

The name introduced so far are

   root_path
   dot_exile
   source_project
   source
   target_project
   target

The root is a full path. I use ~/1/, but other places should work
too. The other names are simple (containing no /). The code will often
want the resolved full path.

    simple
    simple_path

"""

dot_exile = '.exile'

class RunError(Exception):
    def __init__(self, rc, msg):
        self.rc = rc
        self.msg = msg
    def __repr__(self):
        return 'Error %s: %s' % (self.rc, self.msg)

# def find_exile():
#     spath = os.getcwd()
#     while spath != '/': # search towards fs root
#         location = path.join(spath, '.exile')
#         if path.exists(location):
#             return location # found
#         spath = path.dirname(spath)
#     raise RunError(49, 'no .exile/ directory found')

# def find_projects_root():
#     try:
#         root = os.environ('EXILER_ROOT')
#     except KeyError:
#         raise RunError(50, 'no $EXILER_ROOT shell variable set')
#     # root = find_exile()
#     return path.dirname(root)

def projects(root):
    # simple names
    return [p for p in os.listdir(root) if p != '.exile']

# def projects_cmd(args):
#     for i in projects(find_project_root()):
#         print i

# def dot_exile(root):
#     return path.join(root, '.exile')

# def is_project_root(fullpath):
#     r = path.join(fullpath, '.exile')
#     return path.lexists(r) and path.isdir(r)

# def is_project_root_cmd(args):
#     if is_project_root(args.fullpath):
#         return 0
#     else:
#         raise RunError(49, 'no .exile/ directory found')

# def in_project(path=None):
#     """True if the pwd is at the top-level within a project"""
#     path = path or os.getcwd()
#     e = path.join(path.dirname(path), '.exile')
#     return path.lexists(e) and path.isdir(e)

# def shadows(root, fullpath=False):
#     """A shadow directory has the same name as a project
#     directory. The shadow directory exists only if the original
#     project directory as exiled some directories."""
#     def aux():
#         for f in os.listdir(dot_exile(root)):
#             (yield path.join(dot_exile(root), f)) if fullpath else (yield f)
#     return list(aux())

# def shadows_cmd(args):
#     for i in shadows(args.root, arg.long):
#         print i
#     return 0

def folders(root, project, fullpath=False):
    """The exiled target directories for this project"""
    def aux():
        loc = path.join(root, dot_exile, project)
        if path.exists(loc): # A project may have nothing exiled
            for f in os.listdir(loc):
                if fullpath:
                    yield loc, project, f
                else:
                    yield f
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
    We have a projects root directory. Its childen are project
    directories and a .exile directory. The args.source is the name of
    some subdirecory that is immediately under a project directory.
    
    args.root_path - 
    args.project - simple name (pwd)
    args.source - simple name
    """

    if path.sep in args.source:
        raise RunError(19, 'source must be a local directory')
    
    if not path.isdir(args.root_path):
        raise RunError(9, 'no root_path to projects directory given')

    project_path = path.join(args.root_path, args.project)
    if not path.isdir(project_path):
        raise RunError(53, 'project %s directory not found' % project_path)
    
    target_project_path = path.join(args.root_path, dot_exile, args.project)
    
    target_path = path.join(args.root_path, dot_exile, args.project, args.source)
    
    source_path = path.join(args.root_path, args.project, args.source)
    if not path.exists(source_path):
        raise RunError(18, 'source %s not found' % source_path)
    if path.islink(source_path):
        raise RunError(17, 'source %s may not be a symbolic link' % source_path)
    if not path.isdir(source_path):
        raise RunError(16, 'source %s must be a local directory' % source_path)
    
    if not path.exists(target_project_path):
        os.mkdir(target_project_path)
        
    shutil.move(source_path, target_path)
    os.symlink(target_path, source_path)
    return 0

def pardon(args):
    "Restore the exiled directory."
    
    if not path.isdir(args.root_path):
        raise RunError(9, 'no root_path to projects directory given')

    dot_exile_path = path.join(args.root_path, dot_exile)
    if not path.isdir(dot_exile_path):
        raise RunError(49, 'no .exile directory found: %s' % dot_exile_path)

    project_path = path.join(args.root_path, args.project)
    if not path.isdir(project_path):
        raise RunError(53, 'project %s directory not found' % project_path)

    target_project_path = path.join(args.root_path, dot_exile, args.project)
    if not path.isdir(project_path):
        raise RunError(55, 'target project %s directory not found' % target_project_path)
    
    source_path = path.join(args.root_path, args.project, args.source)
    if not path.islink(source_path):
        raise RunError(38 ,'source path %s must be a symbolic link' % source_path)

    target_path = os.readlink(source_path)
    if args.source != path.basename(target_path):
        msg = 'source %s is not the basename form of the exiled (target) directory'
        raise RunError(39, msg % args.source)
    
    if path.dirname(target_path) != target_project_path:
        msg = 'target project %s does not point to a .exile location %s'
        raise RunError(54, msg % (path.dirname(target_path), target_project_path))
    
    os.remove(source_path)
    shutil.move(target_path, source_path)
    
    # Remove exiled project folder if empty
    if os.listdir(target_project_path) == []:
        os.rmdir(target_project_path)
    return 0

def parse_commandline():
    # ---  parent parser for common args  ---
    pp = argparse.ArgumentParser(add_help=False)
    pp.add_argument(
        '-r', '--root_path',
        default = os.environ.get('EXILER_ROOT', None),
        help = 'Fullpath to all projects root.')
    pp.add_argument(
        '-p', '--project',
        default = path.basename(os.getcwd()),
        help = ('Simple name of a project directory that is seen in the projects root.'
              + ' Defaults to the pwd.'))
    
    parser = argparse.ArgumentParser(description='Exiler commands')
    subparsers = parser.add_subparsers()
    
    # ---  exile  ---
    p = subparsers.add_parser(
        'exile',
        parents = [pp],
        help='Move source to .exile/proj/source') 
    p.add_argument(
        'source',
        help='Simple name of subdir with the project')
    p.set_defaults(func=exile)
    
    # ---  pardon  ---
    p = subparsers.add_parser(
        'pardon',
        parents = [pp],
        help='Move target of linkname back to pwd')
    p.add_argument(
        'source',
        help='Simple name of symlink within the pwd that points to an exiled subdir')
    p.set_defaults(func=pardon)
    
    return parser.parse_args(sys.argv[1:])

    # # ---  projects  ---
    # p = subparsers.add_parser(
    #     'projects',
    #     help='list project found from pwd')
    # p.set_defaults(func=projects_cmd)
    
def main():
    try:
        args = parse_commandline()
        rc = args.func(args)
    except RunError, e:
        print >>sys.stderr, e.msg
        rc = e.rc
    return rc

# args = parse_commandline()
# print args
# rc = args.func(args)
# print rc


