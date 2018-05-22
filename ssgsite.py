import os
import glob
import configparser

from datetime import datetime
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader, select_autoescape
import jinja2
import frontmatter

"""
[ABBZUG]
templates = templates
"""

class Site:
    CONFIG_DEFAULTS = {
        'debug': False
    }   # TODO: Make defaults work.


    def __init__(self, contentdir):
        self.load_config(contentdir)
        td = self.config["ABBZUG"].get('templates', 'templates')
        od = self.config["ABBZUG"].get('output', 'output')
        cd = self.config["ABBZUG"].get('content', 'content')
        sd = self.config["ABBZUG"].get('static', 'static')
        self.dir_content = os.path.join(contentdir, cd)
        self.dir_templates = os.path.join(contentdir, td)
        self.dir_output = os.path.join(contentdir, od)
        self.dir_static = os.path.join(contentdir, sd)

        self.jinja2env = Environment(
            loader=FileSystemLoader(self.dir_templates),
            extensions=['jinja2_markdown.MarkdownExtension', 'mdcontent.MDContentExtension']
        )
        self.debug = self.config.get('ABBZUG', 'debug', fallback=False)


    def load_config(self, contentdir):
        """Load the configuration file for a site."""

        fn = os.path.join(contentdir, 'site.conf')
        config = configparser.ConfigParser(defaults=self.CONFIG_DEFAULTS)
        config.read(fn)
        if "ABBZUG" not in config.sections():
            raise ValueError("site.conf is not a valid ABBZUG config file. Needs ABBZUG section.")

        self.config = config


    def build(self):
        """Build an entire site."""

        sitename = self.config.get('ABBZUG', 'sitename', fallback="UNKNOWN")
        if sitename == "UNKNOWN":
            print("[Hint: Set sitename to the name of your site in the config file!]")
        print("Building site %s..." % sitename)
        stime = datetime.now()

        self.cache = {}
        for section in self.config.sections():
            if section[:1] == '/':
                self._preload_section(section[1:], self.config[section])
        print("[PRELOAD] Done")

        for section in self.config.sections():
            if section[:1] == '/':
                location = section[1:]
                print("[LOCATION] /%s" % location)
                self._build_section(location, self.config[section])

        self._copy_static()

        etime = datetime.now()
        elapsed = etime - stime
        print("Building site %s took %s." % (sitename, elapsed))


    def _build_section(self, location, conf):
        """Build a section of a site based on its section configuration."""

        template = conf.get('template', None)
        if not template:
            raise ValueError("Unable to build section %s: No template specified." % (location))

        content = conf.get('content', None)
        index = conf.get('index', None)
        template_file = os.path.join(self.dir_templates, template)
        if content:
            dir_content = os.path.join(self.dir_content, content)
            posts = self._build_content(location, content, template, conf)
            if index:
                # Build an index!
                env = {'posts': self.cache[location].values()}
                self._build_nocontent(location, index, conf, env)
        else:
            if not content and self.debug:
                print("  Warning: This section has no content!")
            self._build_nocontent(location, template, conf)


    def _build_nocontent(self, location, template, conf, env={}):
        """Build a postless (no-content) section."""

        outdir = os.path.join(self.dir_output, location)
        os.makedirs(outdir, exist_ok=True)
        index = os.path.join(outdir, "index.html")

        if self.debug:
            print("  Building template '%s' as '%s'" % (template, index))
        try:
            template = self.jinja2env.get_template(template)
        except jinja2.exceptions.TemplateNotFound as e:
            print("  ERROR: Could not find template '%s'. Skipping!" % (template))
            return
        with open(index, "w+") as fh:
            env.update({
                'section': conf,
                'config': self.config
            })
            fh.write(self._render(template, env))


    def _preload_section(self, location, conf):
        content = conf.get('content', None)
        if not content:
            return

        indir = os.path.join(self.dir_content, content)
        if self.debug:
            print("  Searching for content in %s" % indir)

        self.cache[location] = {}
        for infile in glob.iglob(indir + '/**/*.md', recursive=True):
            infn = infile.split("/")[-1]
            post = frontmatter.load(infile)
            self.cache[location][infn] = post

    def _build_content(self, location, content, template, conf, env={}):
        """Build a section that has associated Markdown posts."""

        #indir = os.path.join(self.dir_content, content)
        outdir = os.path.join(self.dir_output, location)
        #if self.debug:
        #    print("  Searching for content in %s" % indir)
        os.makedirs(outdir, exist_ok=True)

        #posts = []

        for infn, post in self.cache[location].items():
            jinja2env = Environment(
                loader=FileSystemLoader(self.dir_templates),
                extensions=['jinja2_markdown.MarkdownExtension', 'mdcontent.MDContentExtension']
            )
            try:
                template = jinja2env.get_template(template)
            except jinja2.exceptions.TemplateNotFound as e:
                print("  ERROR: Could not find template '%s'. Skipping all content!" % (template))
                return

            outfn = infn.replace(".md", ".html")
            outfile = os.path.join(outdir, outfn)
            with open(outfile, "w+") as fh:
                env.update({
                    'CONTENT': post.content,
                    'post': post.metadata,
                    'section': conf,
                    'config': self.config
                })
                html = self._render(template, env)
                fh.write(html)

            if self.debug:
                print("    %s -> %s" % (infn, outfile))


    def _render(self, template, env={}):
        # TODO: Make render errors pretty.
        #try:
        return template.render(**env)
        #except jinja2.exceptions.UndefinedError as e:
        #    print("%s in template %s:%d" % (e, e.__traceback__.tb_next, e.__traceback__.tb_lineno))
        #    return ""


    def _copy_static(self):
        """Copy static files."""

        print("[STATIC] Copying...")
        static_output = self.config["ABBZUG"].get("static_directory", "")
        static_output = os.path.join(self.dir_output, static_output)
        copy_tree(self.dir_static, static_output)
