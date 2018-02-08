#!/home/crthomas/.virtualenvs/xunit_tools/bin/python

from xunit_parse import XUnitParse

root = '/home/crthomas/scratch/'
xml_in = '{}broken.xml'.format(root)

parser = XUnitParse(xml_in)
parser.parse()
