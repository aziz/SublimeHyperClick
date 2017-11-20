# -*- coding: utf-8 -*-
import re
from os import path


class JstlPathResolver:
    def __init__(self, view, str_lookup, current_dir, roots, lang, settings):
        self.view = view
        self.import_line_regex = settings.get('import_line_regex', {})[lang]
        prog = re.compile(self.import_line_regex[0])
        regMatch = prog.match(str_lookup)
        #print(regMatch.group(1))
        self.str_path = regMatch.group(2)
        self.str_file = regMatch.group(3)
        #print(self.str_path)
        #print(self.str_file)
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        self.dirs_regex = settings.get('lookup_paths', {})[lang]
        self.vendors = settings.get('vendor_dirs', {})[lang]

    def resolve(self):
        for regex_str in self.dirs_regex:
            regions = self.view.find_all(regex_str)
            for region in regions:
                file_path = self.find_folder(region)
                if file_path:
                    return file_path
        return ''

    def find_folder(self, region):
        text = self.view.substr(region)
        #print(text)
        matched = self.is_valid_line(text)
        #print("match 1:")
        #print(matched.group(1))
        #print("match 2:")
        #print(matched.group(2))
        #print(self.str_path)
        #print(self.str_file)
        if matched:
            if matched.group(1) == self.str_path:
                complete_path = matched.group(2) + "/" + self.str_file + ".tag"
                file_path = path.realpath(path.join(self.current_dir, self.str_path))
                for vendor in self.vendors:
                    base_dir = re.split(vendor,file_path)
                    #print("base dir:")
                    #print(base_dir)
                    dest_file_path = base_dir[0] + complete_path
                    #print("final dir:")
                    #print(dest_file_path)
                    if path.isfile(dest_file_path):
                        return dest_file_path
        return ''

    def is_valid_line(self, line_content):
        for regex_str in self.dirs_regex:
            pattern = re.compile(regex_str)
            matched = pattern.match(line_content)
            if matched:
                return matched
        return False