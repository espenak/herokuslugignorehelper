import argparse
import os
import os.path
from fnmatch import fnmatch


class PatternParser(object):
    def __init__(self, pattern, rootdir):
        self.patternraw = pattern
        self.rootdir = rootdir
        self.pattern = self._normalize_pattern(pattern)

    def _normalize_pattern(self, pattern):
        if pattern.startswith('/'):
            pattern = os.path.join(self.rootdir, pattern)
        return pattern

    def match(self, basename, path):
        return fnmatch(basename, self.pattern) or fnmatch(basename, path)

    def __str__(self):
        return self.pattern


class Patterns(object):
    def __init__(self, patterns, rootdir):
        self.patternparsers = [PatternParser(pattern, rootdir) \
            for pattern in patterns.split('\n')]

    def match(self, basename, path):
        for patternparser in self.patternparsers:
            if patternparser.match(basename, path):
                return True
        return False


class IgnoredBase(object):
    def __init__(self, path):
        self.path = path

class IgnoredFile(IgnoredBase):
    def __str__(self):
        return '[F] {}'.format(self.path)

    @property
    def diskspace(self):
        return os.path.getsize(self.path)

class IgnoredDir(IgnoredBase):
    def __str__(self):
        return '[D] {}'.format(self.path)

    @property
    def diskspace(self):
        size = 0
        for root, dirs, files in os.walk(self.path):
            size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
        return size


class SlugIgnore(object):
    def __init__(self, slugignorefile='.slugignore'):
        self.slugignorefile = slugignorefile
        self.rootdir = os.path.abspath(os.path.dirname(self.slugignorefile))
        self.patternsraw = open(self.slugignorefile, 'rb').read()
        self.patterns = Patterns(self.patternsraw, self.rootdir)

    def find_ignored(self):
        ignored_items = []
        for root, dirs, files in os.walk(self.rootdir):

            ignored_dirs = []
            for dirname in dirs:
                if dirname == '.git':
                    ignored_dirs.append(dirname)
                else:
                    path = os.path.join(root, dirname)
                    if self.patterns.match(dirname, path):
                        ignored_dirs.append(dirname)
                        ignored_items.append(IgnoredDir(path))
            for dirname in ignored_dirs:
                # Remove ignored dirs (avoid walking them)
                dirs.remove(dirname)

            for filename in files:
                path = os.path.join(root, filename)
                if self.patterns.match(filename, path):
                    ignored_items.append(IgnoredFile(path))
        return ignored_items


def bytes_to_mb(bytes):
    return float(bytes) / 2**20


def cli():
    parser = argparse.ArgumentParser(description='Create and show the results of ignore files.')
    parser.add_argument('action', metavar='ACTION')
    parser.add_argument('slugignorefile', metavar='SLUGIGNORE', default='.slugignore')

    args = parser.parse_args()
    slugignore = SlugIgnore(args.slugignorefile)
    if args.action == 'listignored':
        for ignoredfile in slugignore.find_ignored():
            print ignoredfile
    elif args.action == 'diskspace':
        ignoredfiles = [(ignoredfile.diskspace, ignoredfile) for ignoredfile in slugignore.find_ignored()]
        ignoredfiles.sort(lambda a, b: cmp(a[0], b[0]))
        ignored_diskspace = 0
        for diskspace, ignoredfile in ignoredfiles:
            print '{:7.3f}Mb {}'.format(bytes_to_mb(diskspace), ignoredfile)
            ignored_diskspace += diskspace
        print 'Ignored {:.1f}Mb in total'.format(bytes_to_mb(ignored_diskspace))
    else:
        raise SystemExit('Invalid action. Use one of: listignored, diskspace')