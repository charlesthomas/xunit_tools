import os.path

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

class BaseObject(object):
    @property
    def version(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as fin:
                return fin.readline().strip()
        except:
            return 'UNKNOWN'

class HTMLObject(BaseObject):
    filename      = None
    render_kwargs = None
    template      = None
    title         = None

    def generate_html(self, destination=None):
        self.validate()
        self.render_kwargs.update(title=self.title, version=self.version)
        path = '{}.html'.format(self.filename)
        if destination is not None:
            path = os.path.join(os.path.expanduser(destination), path)

        # so jinja can find macro.html
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment()
        env.loader = FileSystemLoader(template_dir)
        html = env.get_template('{}.html'.format(self.template))

        with open(path, 'w') as outfile:
            outfile.write(html.render(**self.render_kwargs).encode('utf8'))

    def validate(self):
        for not_none in ['filename', 'render_kwargs', 'template', 'title']:
            assert getattr(self, not_none) is not None, \
            '{} *MUST* be overloaded in the Child Class'.format(not_none)
