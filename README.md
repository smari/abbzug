# Abbzug

> Lifting her lovely and longing face towards the inaudible chant of the sun, she drifted through her time, through space, through the concatenate cells of her unfolding self. Where to now, Abbzug?
>
> (from *The Monkey Wrench Gang* by Edward Abbey)



Abbzug is a static site generator. It tries to make life very simple by not complicating things unnecessarily, while also being pretty radical when that [Glen Canyon Dam](https://wordpress.org/) is taunting you.

I made Abbzug to scratch an itch. Most SSG's have rather annoying templating systems and or are surprisingly difficult to coax into doing certain things. While Jekyll and Hugo are both fine for their purposes, I wanted something a little bit more flexible and familiar.

This is very young software. There are a number of very good features SSG's generally have, such as data directories, more nuanced static collection, and so on, that this doesn't yet have. But it does most of what I need it to already.

## Installation

For now, there is no package available.

```shell
$ git clone https://github.com/smari/abbzug.git
$ cd abbzug
$ pip install -r requirements.txt
```

Now you can run it with:

```shell
$ python abbzug.py
```

## Setting up a site

Create a basic site template:

```shell
$ abbzug newsite mysite/
```

This takes several options:

* *sitename*  ─ the name of your site
* *template_dir* ─ the directory templates should be sought from (defaults to `templates/`)
* *output_dir* ─ the directory your HTML site should be written to (defaults to `output/`)
* *static_dir* ─ the directory static files (such as CSS, Javascript and images) should be collected from (defaults to `static/`)
* *post_dir* ─ the directory Markdown posts should be found in (defaults to `posts/`)

Once you're done running this command, you should edit `mysite/site.conf` and check its settings. There you can define more sections if you want, or fiddle with other settings.

### Sections

Sections are how Abbzug organizes different content. The most simple site only needs a single section, but by using sections to separate out your content you can use a variety of different templates around the site, have different content areas, and create multi-language support.

By default a single section is defined in a generated config. In `mysite/site.conf` it looks like this:

```ini
[/]
index_template = index.html
post_template = post.html
tag_template = tags.html
post_subdir = posts/
tag_subdir = tags/
```

The name of the section indicates where in the hierarchy of your site generated content should end up. All paths are relative to your site root, regardless of where that is. So section `[/]` is the root section of your site. *You will almost always want to have a root section.*

Here we define a few variables:

* *index_template* ─ this is the name of the template you will use to generate this section's index.
* *post_template* ─ this is the template you will use to generate each of this section's posts.
* *tag_template* ─ this is the template you will use to generate each tag page for each tag. (Optional)
* *post_subdir* ─ the subdirectory of your globally defined `post_dir` that contains this section's Markdown content. (Optional: If you leave this out, this section will be considered to be a content-free section and only end up with an index).
* *tag_subdir* ─ the subdirectory of the output directory that tag pages will end up in. (Will only be used if you have one or more tags in this section).

You can define any other variables you wish in the section and they will be available to the templates as variables.

#### Sections for a multilingual site

There are a few ways to do this. The easiest way is, in your sections, to define a language variable for different sections:

```ini
[/is]
...
lang = is

[/en]
...
lang = en
```

And then use the same templates in each section with *i18n* support turned on to deal with the rest of the details. You would naturally either have different content dirs as needed, or point both sections to the same content subdirectory and then have the templates take care of filtering the pages out on the basis of their frontmatter.

### Templates

Abbzug uses the Jinja2 templating engine. If you're familiar with Django, then you'll feel right at home.

A simple template for a page index could look like this, for example:

```jinja2
<html>
<head>
   <title>{{site.sitename}}</title>
</head>
<body>
<ul>
{% for post in posts %}
<li><a href="{{post.url}}">{{post.title}}</a></li>
{% endfor %}
</ul>
</body>
</html>
```

Of course, you may want to use more of Jinja2's advanced features to build a hierarchy of templates and such. Refer to the [Jinja2 documentation](http://jinja.pocoo.org/docs/2.10/) for details.

For the individual posts, you need to tell the template where to insert the compiled Markdown. So you might end up with something like this:

```jinja2
{% extends "layout.html" %}
{% block content %}

<h1>{{post.title}}</h1>

<div id="post-content">
{% abbzug_markdown CONTENT %}
</div>

{% endblock %}
```



**Advanced note:** `CONTENT` is an internal variable containing the Markdown code itself, and `{% abbzug_markdown %}` is a template tag that will convert it to HTML in a nice way. You can technically pass any content to that template tag, or use the `CONTENT` variable in some other way if you want, but there's not really any super good reason to do so for most users.



### Building your site

Now that you've set everything up, you can build your site like so:

```shell
$ abbzug build mysite/
```

The output will end up in your output directory. Just upload that to your hosting provider or do whatever it is you want to do with it.

If you just want to test it locally, one way you can do that is by running a local server on the output directory:

```shell
$ cd mysite/output/
$ python -m http.server
```



## Serve-mode

If you're developing your site, it will get super tedious to continuously rebuild by hand after each minor change. Then the **serve** mode is for you!

If you run:

```shell
$ abbzug serve mysite/
```

Abbzug will keep track of your site directory and if any files change, it will automatically rebuild.



## Authors

* Smári McCarthy <smari at smarimccarthy.is>



## Copyright

Abbzug ─ a Static Site Generator

Copyright © 2018 Smári McCarthy

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

