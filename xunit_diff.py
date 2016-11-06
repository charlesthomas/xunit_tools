import os.path

from jinja2 import Template

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
        self.differences  = self.calculate_differences()
        self.matches      = self.calculate_matches()

        self.total_count  = len(self.union)
        self.a_only_count = len(self.a_only)
        self.b_only_count = len(self.b_only)
        self.diff_count   = len(self.differences)
        self.match_count  = len(self.matches)

    def calculate_differences(self):
        return [case for case in self.intersection if \
                self.a_suite.cases[case].result_type != \
                self.b_suite.cases[case].result_type]

    def calculate_matches(self):
        return [case for case in self.intersection if \
                self.a_suite.cases[case].result_type == \
                self.b_suite.cases[case].result_type]

    @property
    def filename(self):
        name = "{}_vs_{}.html".format(self.a_suite.name, self.b_suite.name)
        return name.lower().replace(' ', '_')

    def generate_html(self, destination=None):
        path = self.filename
        if destination is not None:
            path = os.path.join(os.path.expanduser(destination), path)
        template = os.path.join(os.path.dirname(__file__),
                                'templates', 'xdiff.html')
        html = Template(open(template).read())

        with open(path, 'w') as outfile:
            outfile.write(html.render(diff=self).encode('utf8'))
