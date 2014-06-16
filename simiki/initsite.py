#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os
import os.path
import sys
import shutil
import logging

from simiki.configs import parse_configs
from simiki.log import logging_init
from simiki.utils import (copytree, mkdir_p, listdir_nohidden)


class InitSite(object):

    def __init__(self, config_file, target_path):
        self.config_file = config_file
        if not os.path.exists(self.config_file):
            logging.error("{} not exists".format(self.config_file))
            sys.exit(1)
        try:
            self.configs = parse_configs(self.config_file)
        except Exception as e:
            logging.error(str(e))
        self.source_path = os.path.dirname(__file__)
        self.target_path = target_path

    def get_file(self, src, dst):
        if os.path.exists(dst):
            logging.warning("{} exists".format(dst))
            return

        # Create parent directory
        dst_directory = os.path.dirname(dst)
        if not os.path.exists(dst_directory):
            mkdir_p(dst_directory)
            logging.info("Creating directory: {}".format(dst_directory))

        try:
            shutil.copyfile(src, dst)
            logging.info("Creating config file: {}".format(dst))
        except (shutil.Error, IOError), e:
            logging.error(str(e))

    def get_config_file(self):
        dst_config_file = os.path.join(self.target_path, "_config.yml")
        self.get_file(self.config_file, dst_config_file)

    def get_fabfile(self):
        src_fabfile = os.path.join(
            self.source_path,
            "conf_templates",
            "fabfile.py"
        )
        dst_fabfile = os.path.join(self.target_path, "fabfile.py")
        self.get_file(src_fabfile, dst_fabfile)

    def get_first_page(self):
        nohidden_dir = listdir_nohidden(
            os.path.join(self.target_path, "content")
        )
        # If there is directory under content, do not create first page
        if next(nohidden_dir, False):
            return

        src_fabfile = os.path.join(
            self.source_path,
            "conf_templates",
            "gettingstarted.md"
        )
        dst_fabfile = os.path.join(
            self.target_path,
            "content",
            "intro",
            "gettingstarted.md"
        )
        self.get_file(src_fabfile, dst_fabfile)

    def get_default_theme(self, theme_path):
        src_theme = os.path.join(self.source_path, "themes")
        if os.path.exists(theme_path):
            shutil.rmtree(theme_path)

        copytree(src_theme, theme_path)
        logging.info("Copying default theme to: {}".format(theme_path))

    def init_site(self):
        content_path = os.path.join(self.target_path, self.configs["source"])
        output_path = os.path.join(self.target_path,
                                   self.configs["destination"])
        theme_path = os.path.join(self.target_path, "themes")
        for path in (content_path, output_path, theme_path):
            if os.path.exists(path):
                logging.warning("{} exists".format(path))
            else:
                os.mkdir(path)
                logging.info("Creating directory: {}".format(path))

        self.get_config_file()
        self.get_fabfile()
        self.get_first_page()
        self.get_default_theme(theme_path)
