#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from optparse import OptionParser
from sys import exit, stderr
from textwrap import dedent

from render_objects import BaseObject
from xunit_diff import XUnitDiff
from xunit_parse import XUnitParse

class XUnitTools(BaseObject):
    def __init__(self):
        self.flags = None
        self.files = None
        self.opts  = None

        self.description = dedent('''
            %prog can convert/generate XUnit XML files into HTML reports, and/or
            diff two XUnit XML files and generate an HTML report of the diff''')

        self.usage = ('%prog [--diff] [--diff-only] '
                      '[--destination=/path/to/output/dir/] file [file ...]')

    def err(self, message, code=1):
        size = len(message) + 4
        message = "\n{ex}\n! {m} !\n{ex}\n".format(ex="!"*size, m=message.upper())
        print(message, file=stderr)
        self.opts.print_help()
        exit(code)

    def get_opts(self):
        self.opts = OptionParser(usage=self.usage, version=self.version,
                                 description=self.description.lstrip())
        self.opts.add_option('-d', '--diff', action='store_true', default=False,
                             help='generate a diff of exactly two files')
        self.opts.add_option('-x', '--diff-only', action='store_true', default=False,
                             help='generate diffs, but not regular HTML files')
        self.opts.add_option('-o', '--destination', default=None,
                             help='path to write files (Defaults to .)')
        self.flags, self.files = self.opts.parse_args()
        num = len(self.files)
        if num == 0:
            self.err('you must specify file(s) to convert/diff', 3)
        if self.flags.diff and num != 2:
            self.err('you must specify exactly two files to diff', 4)

    def run(self):
        self.get_opts()
        parsers = [XUnitParse(f) for f in self.files]
        suites = [p.parse() for p in parsers]
        if not self.flags.diff_only:
            [p.generate_html(self.flags.destination) for p in parsers]
        if self.flags.diff:
            diff = XUnitDiff(suites[0], suites[1])
            diff.generate_html(self.flags.destination)

def main():
    XUnitTools().run()

if __name__ == '__main__':
    main()
