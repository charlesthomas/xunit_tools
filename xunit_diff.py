import os.path

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

class XUnitDiff(object):
    def __init__(self, a_suite, b_suite):
        self.a_suite = a_suite
        self.a_cases = set(self.a_suite.cases.keys())

        self.b_suite = b_suite
        self.b_cases = set(self.b_suite.cases.keys())

        self.union        = self.a_cases | self.b_cases
        self.intersection = self.a_cases & self.b_cases
        self.a_only       = self.a_cases - self.b_cases
        self.b_only       = self.b_cases - self.a_cases
        self.good         = self.passed_in_both()
        self.bad          = self.intersection - self.good

        self.total_count  = len(self.union)
        self.a_only_count = len(self.a_only)
        self.b_only_count = len(self.b_only)
        self.good_count   = len(self.good)
        self.bad_count    = len(self.bad)

    @property
    def filename(self):
        name = "{}_vs_{}".format(self.a_suite.filename, self.b_suite.filename)
        return name.lower().replace(' ', '_')

    def passed_in_both(self):
        ret = set()
        good = ['Passed', 'Skipped']
        for case in self.intersection:
            if  self.a_suite.cases[case].result_type in good \
            and self.b_suite.cases[case].result_type in good:
                ret.add(case)
        return ret

    def generate_html(self, destination=None):
        path = '{}.html'.format(self.filename)
        if destination is not None:
            path = os.path.join(os.path.expanduser(destination), path)

        # so jinja can find macro.html
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment()
        env.loader = FileSystemLoader(template_dir)
        html = env.get_template('xdiff.html')

        with open(path, 'w') as outfile:
            outfile.write(html.render(diff=self).encode('utf8'))
