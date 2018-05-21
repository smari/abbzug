import click

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


if __name__ == "__main__":
    cli()
