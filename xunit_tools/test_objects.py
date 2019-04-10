from cgi import escape

class TestCase(object):
    def __init__(self, classname, name, time, **kwargs):
        self.classname = escape(classname)
        self.name      = escape(name)
        self.time      = float(time)
        self.result    = None

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

    @property
    def result_type(self):
        return self.result.rtype.title()


class DidNotRun(TestCase):
    def __init__(self, test_case):
        self.classname   = test_case.classname
        self.name        = test_case.name
        self.time        = float(0)
        self.result      = TestResult("Did Not Run")


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
        key = "{}.{}".format(testcase.classname, testcase.name)
        self.cases[key] = testcase
        return testcase

    def cases_by_result(self, result):
        return [case for case in self.cases.keys() if \
                result == self.cases[case].result_type]

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
