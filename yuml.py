#######################################################################
#
# Copyright (C) 2013, Chet Luther <chet.luther@gmail.com>
#
# Licensed under GNU General Public License 3.0 or later.
# Some rights reserved. See COPYING, AUTHORS.
#
#######################################################################

'''
All Sublime Text plugins functionality for yUML is contained in this
file.

yUML is an online tool for creating and publishing simple UML diagrams.
It's makes it really easy for you to:

* Embed UML diagrams in blogs, emails and wikis.
* Post UML diagrams in forums and blog comments.
* Use directly within your web based bug tracking tool.
* Copy and paste UML diagrams into MS Word documents and Powerpoint
  presentations.
'''

import sublime
import sublime_plugin
import webbrowser


DEFAULT_TYPE = 'class'
DEFAULT_EXTENSION = 'png'
DEFAULT_STYLE = 'scruffy'
DEFAULT_DIR = 'LR'
DEFAULT_SCALE = '100'

VALID_TYPES = ('activity', 'class', 'usecase')
VALID_EXTENSIONS = ('jpg', 'json', 'pdf', 'png', 'svg')
VALID_STYLES = ('nofunky', 'plain', 'scruffy')
VALID_DIRS = ('LR', 'RL', 'TB')


def selected_or_all(view):
    '''
    Return all selected regions or everything if no selections.

    Selections will be concatenated with newlines.
    '''
    if all([region.empty() for region in view.sel()]):
        return view.substr(sublime.Region(0, view.size()))

    return '\n'.join([view.substr(region) for region in view.sel()])


class YumlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = self.view.settings()
        yuml = Yuml(
            dsl=selected_or_all(self.view),
            type=settings.get('default_type', DEFAULT_TYPE),
            extension=settings.get('default_extension', DEFAULT_EXTENSION),
            customisations={
                'style': settings.get('default_style', DEFAULT_STYLE),
                'dir': settings.get('default_dir', DEFAULT_DIR),
                'scale': settings.get('default_scale', DEFAULT_SCALE),
                })

        webbrowser.open_new_tab(yuml.url)


class Yuml(object):
    '''
    Represents all options in a yUML URL.
    '''

    dsl = None
    customisations = None
    type = None
    extension = None

    def __init__(self, dsl, customisations=None, type=DEFAULT_TYPE, extension=DEFAULT_EXTENSION):
        self.dsl = ', '.join(dsl.strip().splitlines())

        if customisations is None:
            self.customisations = YumlCustomisations()
        elif isinstance(customisations, dict):
            self.customisations = YumlCustomisations(**customisations)
        elif isinstance(customisations, YumlCustomisations):
            self.customisations = customisations
        else:
            raise ValueError(
                "invalid value for customsations: {}".format(customisations))

        if type.lower() not in VALID_TYPES:
            raise ValueError(
                "invalid value for type: {}".format(type))
        else:
            self.type = type.lower()

        if extension.lower() not in VALID_EXTENSIONS:
            raise ValueError(
                "invalid value for extension: {}".format(extension))
        else:
            self.extension = extension.lower()

    @property
    def url(self):
        return 'http://yuml.me/diagram/{customisations.url}/{type}/{dsl}.{extension}'.format(**self.__dict__)


class YumlCustomisations(object):
    '''
    Represents the "customisations" option set in a yUML URL.
    '''

    style = None
    dir = None
    scale = None

    def __init__(self, style=DEFAULT_STYLE, dir=DEFAULT_DIR, scale=DEFAULT_SCALE):
        if style.lower() not in VALID_STYLES:
            raise ValueError("invalid value for style: {}".format(style))
        else:
            self.style = style.lower()

        if dir.upper() not in VALID_DIRS:
            raise ValueError("invalid value for dir: {}".format(dir))
        else:
            self.dir = dir.upper()

        try:
            int(scale)
        except TypeError:
            raise TypeError(
                "scale must be a string or a number, not '{}'".format(
                    type(scale)))
        except ValueError:
            raise ValueError("invalid value for scale: {}".format(scale))
        else:
            self.scale = scale

    @property
    def url(self):
        return '{style};dir:{dir};scale:{scale};'.format(**self.__dict__)