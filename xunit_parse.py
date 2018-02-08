import os.path
from cgi import escape
import xml.etree.ElementTree as ElementTree

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from test_objects import TestSuite

class XUnitParse(object):
    def __init__(self, filepath):
        self.suite = None
        self.root = ElementTree.parse(filepath).getroot()
        self.filename = os.path.splitext(os.path.basename(filepath))[0]
        if self.root.attrib.get('name', None) is None:
            self.root.attrib.update(name=self.filename)

    def generate_html(self, destination=None):
        path = '{}.html'.format(self.filename)
        if destination is not None:
            path = os.path.join(os.path.expanduser(destination), path)
        if self.suite is None:
            self.parse()

        # so jinja can find macro.html
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment()
        env.loader = FileSystemLoader(template_dir)
        html = env.get_template('xunit.html')

        with open(path, 'w') as outfile:
            outfile.write(html.render(suite=self.suite).encode('utf8'))

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
        return self.suite
