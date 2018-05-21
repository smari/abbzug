import click
import pyinotify

import ssgsite

ABBZUG_DEBUG = False

@click.group()
@click.option('--debug', type=click.BOOL, default=False)
def cli(debug):
    ABBZUG_DEBUG = debug

@cli.command()
@click.argument("contentdir", type=click.Path(exists=True, dir_okay=True, file_okay=False))
def build(contentdir):
    #try:
    site = ssgsite.Site(contentdir)
    site.build()
    #except Exception as e:
    #    if ABBZUG_DEBUG:
    #        print(e)
    #        print(type(inst))
    #    else:
    #        print("ERROR: %s" % e)

@cli.command()
@click.argument("contentdir", type=click.Path(exists=True, dir_okay=True, file_okay=False))
def serve(contentdir):
    class RebuildHandler(pyinotify.ProcessEvent):
        def my_init(self, site):
            self.site = site

        def process_IN_MODIFY(self, event):
            if self.site.dir_output in event.pathname:
                return
            print("Detected change. Rebuilding:")
            self.site = ssgsite.Site(contentdir)
            self.site.build()

    site = ssgsite.Site(contentdir)
    site.build()

    wm = pyinotify.WatchManager()
    handler = RebuildHandler(site=site)
    excl_lst = ["%s" % site.dir_output]
    excl = pyinotify.ExcludeFilter(excl_lst)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(contentdir, pyinotify.IN_MODIFY, rec=True, auto_add=True, exclude_filter=excl)
    notifier.loop()

if __name__ == "__main__":
    cli()
