# -*- coding: utf-8 -*-
"""
    jinja2_mdcontent
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    A jinja2 extension for ABBZUG that adds a `{% mdcontent %}` tag.
    Based on jinja2_markdown, (c) 2014 by Daniel Chatfield

"""

import markdown
from jinja2.nodes import Output
from jinja2.ext import Extension


class MDContentExtension(Extension):
    tags = set(['abbzug_markdown'])

    def __init__(self, environment):
        super(MDContentExtension, self).__init__(environment)
        environment.extend(
            markdowner=markdown.Markdown(extensions=['extra'])
        )
        self.abzenv = environment

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression()]
        cm = self.call_method('_markdown', args)
        return Output([cm], lineno=lineno)

    def _markdown(self, md):
        self.environment.markdowner.reset()
        out = self.environment.markdowner.convert(md)
        return out
