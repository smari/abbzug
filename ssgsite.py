import os
import glob
import configparser

from datetime import datetime
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
    }

    def __init__(self, contentdir):
        self.load_config(contentdir)
        td = self.config["ABBZUG"].get('templates', 'templates')
        od = self.config["ABBZUG"].get('output', 'output')
        cd = self.config["ABBZUG"].get('content', 'content')
        self.dir_content = os.path.join(contentdir, cd)
        self.dir_templates = os.path.join(contentdir, td)
        self.dir_output = os.path.join(contentdir, od)
        self.jinja2env = Environment(
            loader=FileSystemLoader(self.dir_templates),
            extensions=['jinja2_markdown.MarkdownExtension', 'mdcontent.MDContentExtension']
        )
        self.debug = self.config.get('ABBZUG', 'debug', fallback=False)

    def load_config(self, contentdir):
        fn = os.path.join(contentdir, 'site.conf')
        config = configparser.ConfigParser(defaults=self.CONFIG_DEFAULTS)
        config.read(fn)
        if "ABBZUG" not in config.sections():
            raise ValueError("site.conf is not a valid ABBZUG config file. Needs ABBZUG section.")

        self.config = config

    def build(self):
        sitename = self.config.get('ABBZUG', 'sitename', fallback="UNKNOWN")
        if sitename == "UNKNOWN":
            print("[Hint: Set sitename to the name of your site in the config file!]")
        print("Building site %s..." % sitename)
        stime = datetime.now()
        for section in self.config.sections():
            if section[:1] == '/':
                location = section[1:]
                print("[LOCATION] /%s" % location)
                self.build_section(location, self.config[section])
        etime = datetime.now()
        elapsed = etime - stime
        print("Building site %s took %s." % (sitename, elapsed))

    def build_section(self, location, conf):
        template = conf.get('template', None)
        if not template:
            raise ValueError("Unable to build section %s: No template specified." % (location))

        content = conf.get('content', None)
        template_file = os.path.join(self.dir_templates, template)
        if content:
            dir_content = os.path.join(self.dir_content, content)
            self.build_content(location, content, template)
        else:
            if self.debug:
                print("  Warning: This section has no content!")
            self.build_nocontent(location, template)

    def build_nocontent(self, location, template):
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
            fh.write(template.render())

    def build_content(self, location, content, template):
        indir = os.path.join(self.dir_content, content)
        outdir = os.path.join(self.dir_output, location)
        if self.debug:
            print("  Searching for content in %s" % indir)
        os.makedirs(outdir, exist_ok=True)

        for infile in glob.iglob(indir + '/**/*.md', recursive=True):
            jinja2env = Environment(
                loader=FileSystemLoader(self.dir_templates),
                extensions=['jinja2_markdown.MarkdownExtension', 'mdcontent.MDContentExtension']
            )
            try:
                template = jinja2env.get_template(template)
            except jinja2.exceptions.TemplateNotFound as e:
                print("  ERROR: Could not find template '%s'. Skipping all content!" % (template))
                return

            infn = infile.split("/")[-1]
            post = frontmatter.load(infile)
            outfn = infn.replace(".md", ".html")
            outfile = os.path.join(outdir, outfn)
            with open(outfile, "w+") as fh:
                env = {'CONTENT': post.content, 'post': post.metadata, 'config': self.config}
                fh.write(template.render(**env))

            if self.debug:
                print("    %s -> %s" % (infn, outfile))
