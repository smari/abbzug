import os
import glob
import configparser

from slugify import slugify
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
        td = self.config["ABBZUG"].get('template_dir', 'templates/')
        od = self.config["ABBZUG"].get('output_dir', 'output/')
        sd = self.config["ABBZUG"].get('static_dir', 'static/')
        cd = self.config["ABBZUG"].get('post_dir', 'posts/')
        self.dir_posts = os.path.join(contentdir, cd)
        self.dir_templates = os.path.join(contentdir, td)
        self.dir_output = os.path.join(contentdir, od)
        self.dir_static = os.path.join(contentdir, sd)
        self.base_url = self.config["ABBZUG"].get('base_url', '/')

        self.jinja2env = Environment(
            loader=FileSystemLoader(self.dir_templates),
            extensions=['jinja2_markdown.MarkdownExtension',
                        'abbzug.mdcontent.MDContentExtension',
                        'jinja2.ext.loopcontrols']
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
        self.tags = {}
        for section in self.config.sections():
            if section[:1] == '/':
                self._preload_section(section[1:], self.config[section])
                self._build_tags(section[1:], self.config[section])
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

        post_template = conf.get('post_template', None)
        index_template = conf.get('index_template', None)
        if not index_template:
            raise ValueError("Unable to build section %s: No index template specified." % (location))

        content = conf.get('post_subdir', None)
        if content:
            if not post_template:
                raise ValueError("Unable to build section %s: No post template specified." % (location))

            dir_content = os.path.join(self.dir_posts, content)
            posts = self._build_content(location, content, post_template, conf)

            # Build an index!
            env = {'posts': self.cache[location]}
            self._build_nocontent(location, index_template, conf, env)
        else:
            if not content and self.debug:
                print("  Warning: This section has no content!")
            self._build_nocontent(location, index_template, conf)


    def _build_nocontent(self, location, template, conf, env={}):
        """Build a postless (no-content) section."""

        outdir = os.path.join(self.dir_output, location)
        os.makedirs(outdir, exist_ok=True)
        index = os.path.join(outdir, "index.html")

        if self.debug:
            print("  Building template '%s' as '%s'" % (template, index))

        template = self._get_template(template)
        if not template: return

        with open(index, "w+") as fh:
            env.update({
                'section': conf,
                'section_name': location,
                'config': self.config,
                'site': self.config['ABBZUG'],
                'site_posts': self.cache,
                'tags': self.tags[location],
                'site_tags': self.tags
            })
            fh.write(self._render(template, env))


    def _build_content(self, location, content, template, conf, env={}):
        """Build a section that has associated Markdown posts."""

        for post in self.cache[location]:
            template = self._get_template(template)
            if not template: return

            with open(post.metadata["outpath"], "w+") as fh:
                env.update({
                    'CONTENT': post.content,
                    'post': post.metadata,
                    'site_posts': self.cache,
                    'section': conf,
                    'site': self.config['ABBZUG'],
                    'config': self.config,
                    'tags': self.tags[location]
                })
                html = self._render(template, env)
                fh.write(html)

            if self.debug:
                print("    %s -> %s" % (post.metadata["inpath"], post.metadata["outpath"]))


    def _preload_section(self, location, conf):
        content = conf.get('post_subdir', None)
        self.cache[location] = []
        self.tags[location] = {}
        if not content:
            return

        indir = os.path.join(self.dir_posts, content)
        outdir = os.path.join(self.dir_output, location)
        os.makedirs(outdir, exist_ok=True)

        if self.debug:
            print("  Searching for content in %s" % indir)

        for infile in glob.iglob(indir + '/**/*.md', recursive=True):
            infn = infile.split("/")[-1]
            outfn = infn.replace(".md", ".html")
            outfile = os.path.join(outdir, outfn)
            post = frontmatter.load(infile)
            post.metadata["inpath"] = infile
            post.metadata["outpath"] = outfile
            post.metadata["url"] = self.base_url + location + outfn
            post.metadata["readingtime"] = round(len(str(post).split(" "))/270.0)
            if "tags" not in post.metadata:
                post.metadata["tags"] = {}
            self.cache[location].append(post)
            for tag in post.metadata["tags"]:
                if tag not in self.tags[location]:
                    self.tags[location][tag] = {}
                    self.tags[location][tag]["posts"] = []
                self.tags[location][tag]["posts"].append(post)


    def _build_tags(self, location, conf):
        tag_template = conf.get('tag_template', None)
        tag_subdir = conf.get('tag_subdir', None)
        if location not in self.tags:
            self.tags[location] = {}

        tags = self.tags[location]

        if not (tags and tag_template and tag_subdir):
            return

        outdir = os.path.join(self.dir_output, location, tag_subdir)

        for tag, meta in tags.items():
            meta["tag"] = tag
            meta["slug"] = slugify(tag)
            meta["url"] = self.base_url + os.path.join(location, tag_subdir, meta["slug"]) + '/'

            tagoutdir = os.path.join(outdir, meta["slug"])
            os.makedirs(tagoutdir, exist_ok=True)

            meta["outfile"] = os.path.join(tagoutdir, 'index.html')
            self.tags[location][tag] = meta
            template = self._get_template(tag_template)
            if not template: return
            with open(meta["outfile"], "w+") as fh:
                env = {
                    'config': self.config,
                    'section': conf,
                    'tag': meta,
                    'tagname': tag
                }
                html = self._render(template, env)
                fh.write(html)


    def _get_template(self, template):
        try:
            return self.jinja2env.get_template(template)
        except jinja2.exceptions.TemplateNotFound as e:
            print("  ERROR: Could not find template '%s'." % (template))
            return None

    def _render(self, template, env={}):
        # TODO: Make render errors pretty.
        #try:
        return template.render(**env)
        #except jinja2.exceptions.UndefinedError as e:
        #    print("%s in template %s:%d" % (e, e.__traceback__.tb_next, e.__traceback__.tb_lineno))
        #    return ""


    def _copy_static(self):
        """Copy static files."""

        static_output = self.config["ABBZUG"].get("static_dir", "")
        static_output = os.path.join(self.dir_output, static_output)
        print("[STATIC] Copying to %s." % static_output)
        copy_tree(self.dir_static, static_output)
