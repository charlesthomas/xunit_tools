import os.path
import xml.etree.ElementTree as ElementTree

from jinja2 import Template

from test_objects import TestSuite

class XUnitParse(object):
    def __init__(self, filepath):
        self.suite = None
        self.root = ElementTree.parse(filepath).getroot()
        if self.root.attrib.get('name', None) is None:
            name = os.path.splitext(os.path.basename(filepath))[0]
            self.root.attrib.update(name=name)

    @property
    def filename(self):
        return self.suite.filename

    def generate_html(self, destination=None):
        path = self.filename
        if destination is not None:
            path = os.path.join(os.path.expanduser(destination), path)
        if self.suite is None:
            self.parse()
        template = os.path.join(os.path.dirname(__file__),
                                'templates', 'xunit.html')
        html = Template(open(template).read())
        with open(path, 'w') as outfile:
            outfile.write(html.render(suite=self.suite).encode('utf8'))

    def parse(self):
        self.suite = TestSuite(**self.root.attrib)
        for case in self.root:
            testcase = self.suite.add_case(case)
            passed = True
            for res in case:
                if res.tag == 'system-out':
                    continue
                passed = False
                if res.tag == 'skipped':
                    self.suite.increment_skip()
                testcase.add_result(rtype=res.tag, stacktrace=res.text,
                                    message=res.attrib.get('message', None),
                                    etype=res.attrib.get('type', None))
            if passed:
                testcase.add_result(rtype='passed')
                self.suite.increment_pass()
        return self.suite
