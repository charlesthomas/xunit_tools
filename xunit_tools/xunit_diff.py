from render_objects import HTMLObject
from test_objects import DidNotRun

class XUnitDiff(HTMLObject):
    template = 'xdiff'

    def __init__(self, a_suite, b_suite):
        self.render_kwargs = {'diff': self}

        self.a_suite = a_suite
        self.a_cases = set(self.a_suite.cases.keys())

        self.b_suite = b_suite
        self.b_cases = set(self.b_suite.cases.keys())

        self.union        = self.a_cases | self.b_cases
        self.good         = self.passed_in_both()
        self.bad          = self.union - self.good

        self.total_count  = len(self.union)
        self.good_count   = len(self.good)
        self.bad_count    = len(self.bad)

    @property
    def filename(self):
        return self.title.lower().replace(' ', '_')

    def passed_in_both(self):
        ret = set()
        good = ['Passed', 'Skipped', 'Did Not Run']
        for case in self.union:
            a_case = self.a_suite.cases.get(case, None)
            b_case = self.b_suite.cases.get(case, None)

            if a_case is None:
                self.a_suite.cases[case] = DidNotRun(b_case)
            if b_case is None:
                self.b_suite.cases[case] = DidNotRun(a_case)

            if  self.a_suite.cases[case].result_type in good \
            and self.b_suite.cases[case].result_type in good:
                ret.add(case)
        return ret

    @property
    def title(self):
        return "{} vs {}".format(self.a_suite.filename, self.b_suite.filename)
