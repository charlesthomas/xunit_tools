import os.path
from cgi import escape
import xml.etree.ElementTree as ElementTree

from render_objects import HTMLObject
from test_objects import TestSuite

class XUnitParse(HTMLObject):
    template = 'xunit'

    def __init__(self, filepath):
        self.filepath = filepath
        self.suite = None
        self.root = ElementTree.parse(filepath).getroot()
        if self.root.attrib.get('name', None) is None:
            self.root.attrib.update(name=self.filename)

    @property
    def filename(self):
        return os.path.splitext(os.path.basename(self.filepath))[0]

    def parse(self):
        kwargs = self.root.attrib
        kwargs['filename'] = self.filename
        self.suite = TestSuite(**kwargs)
        for case in self.root:
            testcase = self.suite.add_case(case)
            passed = True
            for res in case:
                if res.tag == 'system-out':
                    continue
                passed = False
                if res.tag == 'skipped':
                    self.suite.increment_skip()
                if res.tag == 'error' and 'AssertionError' in res.text:
                    res.tag = 'failure'
                    self.suite.increment_fail()
                testcase.add_result(rtype=res.tag, stacktrace=escape(res.text),
                                    message=res.attrib.get('message', None),
                                    etype=res.attrib.get('type', None))
            if passed:
                testcase.add_result(rtype='passed')
                self.suite.increment_pass()
        self.render_kwargs = {'suite': self.suite}
        return self.suite

    @property
    def title(self):
        return self.root.attrib['name']
