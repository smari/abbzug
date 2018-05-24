import os

import click
import pyinotify

from abbzug import ssgsite

ABBZUG_DEBUG = False

@click.group()
@click.option('--debug', type=click.BOOL, default=False)
def cli(debug):
    ABBZUG_DEBUG = debug

@cli.command()
@click.argument("site_dir", type=click.Path(exists=True, dir_okay=True, file_okay=False))
def build(site_dir):
    #try:
    site = ssgsite.Site(site_dir)
    site.build()
    #except Exception as e:
    #    if ABBZUG_DEBUG:
    #        print(e)
    #        print(type(inst))
    #    else:
    #        print("ERROR: %s" % e)

@cli.command()
@click.argument("site_dir", type=click.Path(exists=True, dir_okay=True, file_okay=False))
def serve(site_dir):
    class RebuildHandler(pyinotify.ProcessEvent):
        def my_init(self, site):
            self.site = site

        def process_IN_MODIFY(self, event):
            if self.site.dir_output in event.pathname:
                return
            print("Detected change. Rebuilding:")
            self.site = ssgsite.Site(site_dir)
            self.site.build()

    site = ssgsite.Site(site_dir)
    site.build()

    wm = pyinotify.WatchManager()
    handler = RebuildHandler(site=site)
    excl_lst = ["%s" % site.dir_output]
    excl = pyinotify.ExcludeFilter(excl_lst)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(site_dir, pyinotify.IN_MODIFY, rec=True, auto_add=True, exclude_filter=excl)
    notifier.loop()


CONF_TEMPLATE = """
[ABBZUG]
sitename = {sitename}
template_dir = {template_dir}
output_dir = {output_dir}
static_dir = {static_dir}
post_dir = {post_dir}
; base_url = https://www.example.com

[/]
index_template = index.html
post_template = post.html
tag_template = tags.html
; post_subdir = ...
tag_subdir = tags/
"""

@cli.command()
@click.argument("site_dir", type=click.Path(exists=False, dir_okay=True, file_okay=False))
@click.option("--sitename", default="My Site")
@click.option("--template_dir", default="templates/")
@click.option("--output_dir", default="output/")
@click.option("--static_dir", default="static/")
@click.option("--post_dir", default="content/")
def newsite(site_dir, **argv):
    os.makedirs(site_dir)
    with open(os.path.join(site_dir, "site.conf"), "w+") as conf:
        conf.write(CONF_TEMPLATE.format(**argv))

    os.makedirs(os.path.join(site_dir, argv["template_dir"]), exist_ok=True)
    os.makedirs(os.path.join(site_dir, argv["output_dir"]), exist_ok=True)
    os.makedirs(os.path.join(site_dir, argv["static_dir"]), exist_ok=True)
    os.makedirs(os.path.join(site_dir, argv["post_dir"]), exist_ok=True)


if __name__ == "__main__":
    cli()
