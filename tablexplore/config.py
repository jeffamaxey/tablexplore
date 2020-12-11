#!/usr/bin/env python
"""
    Implements a configuration class for pandasqtable
    Created Feb 2019
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from __future__ import absolute_import, division, print_function
import math, time
import os, types
import string, copy
from collections import OrderedDict
try:
    import configparser
except:
    import ConfigParser as configparser
from PySide2 import QtCore, QtGui
from PySide2.QtCore import QObject#, pyqtSignal, pyqtSlot, QPoint
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from . import dialogs

homepath = os.path.join(os.path.expanduser('~'))
configpath = os.path.join(homepath,'.config/pandastable')
if not os.path.exists(configpath):
    try:
        os.makedirs(configpath, exist_ok=True)
    except:
        os.makedirs(configpath)
default_conf = os.path.join(configpath, 'default.conf')

baseoptions = OrderedDict()
baseoptions['base'] = {'font': 'Arial','fontsize':12, 'fontstyle':'',
                        'floatprecision':2,
                        'rowheight':22,'cellwidth':80, 'linewidth':1,
                        'align':'w',
                        }
baseoptions['colors'] =  {'cellbackgr':'#F4F4F3',
                        'textcolor':'black',
                        'grid_color':'#ABB1AD',
                        'rowselectedcolor':'#E4DED4'}
baseoptions['plotting'] = {'marker': '','linestyle':'-',
                        'colormap':'Spectral',
                        'ms':5, 'grid':0
                        }

def write_default_config():
    """Write a default config to users .config folder. Used to add global settings."""

    fname = os.path.join(config_path, 'default.conf')
    if not os.path.exists(fname):
        try:
            #os.mkdir(config_path)
            os.makedirs(config_path)
        except:
            pass
        write_config(conffile=fname, defaults=baseoptions)
    return fname

def write_config(conffile='default.conf', defaults={}):
    """Write a default config file"""

    if not os.path.exists(conffile):
        cp = create_config_parser_from_dict(defaults)
        cp.write(open(conffile,'w'))
        print ('wrote config file %s' %conffile)
    return conffile

def create_config_parser_from_dict(data=None, sections=baseoptions.keys(), **kwargs):
    """Helper method to create a ConfigParser from a dict of the form shown in
       baseoptions"""

    if data is None:
        data = baseoptions
    #print (data)
    cp = configparser.ConfigParser()
    for s in sections:
        cp.add_section(s)
        if not s in data:
            continue
        for name in sorted(data[s]):
            val = data[s][name]
            if type(val) is list:
                val = ','.join(val)
            cp.set(s, name, str(val))

    #use kwargs to create specific settings in the appropriate section
    for s in cp.sections():
        opts = cp.options(s)
        for k in kwargs:
            if k in opts:
                cp.set(s, k, kwargs[k])
    return cp

def update_config(options):
    cp = create_config_parser_from_dict()
    for section in cp.sections():
        for o in cp[section]:
            cp[section][o] = str(options[o])
    return cp

def parse_config(conffile=None):
    """Parse a configparser file"""

    f = open(conffile,'r')
    cp = configparser.ConfigParser()
    try:
        cp.read(conffile)
    except Exception as e:
        print ('failed to read config file! check format')
        print ('Error returned:', e)
        return
    f.close()
    return cp

def get_options(cp):
    """Makes sure boolean opts are parsed"""

    from collections import OrderedDict
    options = OrderedDict()
    #options = cp._sections['base']
    for section in cp.sections():
        options.update( (cp._sections[section]) )
    for o in options:
        for section in cp.sections():
            try:
                options[o] = cp.getboolean(section, o)
            except:
                pass
            try:
                options[o] = cp.getint(section, o)
            except:
                pass
    return options

def print_options(options):
    """Print option key/value pairs"""

    for key in options:
        print (key, ':', options[key])
    print ()

def check_options(opts):
    """Check for missing default options in dict. Meant to handle
       incomplete config files"""

    sections = list(baseoptions.keys())
    for s in sections:
        defaults = dict(baseoptions[s])
        for i in defaults:
            if i not in opts:
                opts[i] = defaults[i]
    return opts

def load_options():
    if not os.path.exists(default_conf):
        write_config(default_conf, defaults=baseoptions)
    cp = parse_config(default_conf)
    options = get_options(cp)
    options = check_options(options)
    return options

def apply_options(options, table):
    """Apply options to a table"""

    for i in options:
        table.__dict__[i] = options[i]
        #print (i, type(options[i]))
    table.setFont()
    table.redraw()
    return
