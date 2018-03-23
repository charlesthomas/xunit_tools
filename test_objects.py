from collections import defaultdict
from cgi import escape
from re import search

class TestResultMatcher(object):
    def __init__(self, name, rtype=None, message_pattern=None, etype_pattern=None):
        self.name = name
        self.rtype = rtype
        self.message_pattern = message_pattern
        self.etype_pattern = etype_pattern

    def is_match(self, result):
        return self.matches_rtype(result) and \
               self.matches_etype(result) and \
               self.matches_message(result)

    def _blank_or_matches(self, haystack, needle):
        if not needle:
            return True

        return search(needle, haystack)

    def matches_rtype(self, result):
        return self.rtype is None or result.rtype == self.rtype

    def matches_etype(self, result):
        return self._blank_or_matches(result.etype, self.etype_pattern)

    def matches_message(self, result):
        return self._blank_or_matches(result.message, self.message_pattern)

class TestCase(object):
    def __init__(self, classname, name, time, **kwargs):
        self.classname = escape(classname)
        self.name      = escape(name)
        self.time      = float(time)
        self.result    = None
        self.suite     = None
        self.groups    = list()

    def classify(self):
        if self.suite and self.result and not self.groups:
            self.groups = self.suite.classify(self.result)

    def __eq__(self, other):
        return self.result == other.result

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "TestCase(classname={}, name={}, time={})".format(
                self.classname, self.name, self.time)

    def __str__(self):
        return self.name

    def add_result(self, rtype, stacktrace=None, message=None, etype=None):
        self.result = TestResult(rtype=rtype, message=message, etype=etype,
                                 stacktrace=stacktrace)
        self.classify()

    @property
    def result_type(self):
        return self.result.rtype.title()

class TestResult(object):
    def __init__(self, rtype, message=None, etype=None, stacktrace=None, **kwargs):
        self.rtype      = rtype
        self.message    = message
        self.etype      = etype
        self.stacktrace = stacktrace

    def __eq__(self, other):
        return self.rtype == other.rtype

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "TestResult(rtype={}, message={}, etype={}, stacktrace={})".format(
                self.rtype, self.message, self.etype, self.stacktrace)

    def __str__(self):
        if self.rtype == 'passed':
            return 'PASSED'
        elif self.rtype == 'skip':
            return self.stacktrace
        elif self.rtype == 'error':
            return "ERROR {}\n{}\n{}".format(self.etype, self.message, self.stacktrace)
        elif self.rtype == 'failure':
            return "FAILURE {}\n{}".format(self.message, self.stacktrace)
        else:
            return self.__repr__()

class TestSuite(object):
    def __init__(self, errors, failures, tests, name, filename, time=None, skip=None, **kwargs):
        self.errors   = int(errors)
        self.failures = int(failures)
        self.tests    = int(tests)
        self.name     = name
        self.filename = filename.lower().replace(' ', '_')
        self.time     = float(time or 0)
        self.passes   = 0
        self.cases    = dict()
        self.matchers = kwargs.get('matchers', list())
        self.group_counts = defaultdict(int)

        if skip is None:
            self.count_skips = True
            self.skips = 0
        else:
            self.skips       = int(skip)
            self.count_skips = False

    def __repr__(self):
        return "TestSuite(errors={}, failures={}, tests={}, time={}, name={})".format(
                self.errors, self.failures, self.tests, self.time, self.name)

    def __str__(self):
        if self.name is None:
            return self.__repr__()
        return self.name

    def add_case(self, case):
        testcase = TestCase(**case.attrib)
        testcase.suite = self
        key = "{}.{}".format(testcase.classname, testcase.name)
        self.cases[key] = testcase
        return testcase

    def cases_by_result(self, result):
        return [case for case in self.cases.keys() if \
                result == self.cases[case].result_type]

    def cases_by_groups(self):
        ret = defaultdict(list)
        for case in self.cases.values():
            for group in case.groups:
                ret[group].append(case)
        
        return ret

    def classify(self, result):
        matches = list()
        for matcher in self.matchers:
            if matcher.is_match(result):
                self.group_counts[matcher.name] += 1
                matches.append(matcher.name)

        return matches

    def increment_fail(self):
        self.failures += 1
        self.errors   -= 1

    def increment_pass(self):
        self.passes += 1

    def increment_skip(self):
        if not self.count_skips:
            return
        self.skips += 1

    @property
    def passed_cases(self):
        return self.cases_by_result('Passed')

    @property
    def skipped_cases(self):
        return self.cases_by_result('Skipped')

    @property
    def errored_cases(self):
        return self.cases_by_result('Error')

    @property
    def failed_cases(self):
        return self.cases_by_result('Failure')
