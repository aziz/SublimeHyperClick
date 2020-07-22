import re
from os import path

dirs_regex = [
    "taglib *prefix ?= ?[\"'](.*)[\"'] *tagdir ?= ?[\"'](.*)[\"']",
    "xmlns:(\\w*)=[\"']urn:jsptagdir:(.*?)[\"']"
]
prog = re.compile('(<([\\w-]*)\\:([\\w-]*))')

# TEMP: hardcoded settings
class JstlPathResolver:
    def __init__(self, view, str_lookup, current_dir, roots, settings):
        self.view = view
        regMatch = prog.match(str_lookup)
        self.str_path = regMatch.group(2)
        self.str_file = regMatch.group(3)
        self.current_dir = current_dir
        self.settings = settings
        self.roots = roots

        self.valid_extensions = ['jsp', 'tag']
        self.vendors = ['WEB-INF']

    def resolve(self):
        for regex_str in dirs_regex:
            regions = self.view.find_all(regex_str)
            for region in regions:
                file_path = self.find_folder(region)
                if file_path:
                    return file_path
        return ''

    def find_folder(self, region):
        text = self.view.substr(region)
        matched = self.is_valid_line(text)
        if matched:
            if matched.group(1) == self.str_path:
                complete_path = matched.group(2) + "/" + self.str_file + ".tag"
                file_path = path.realpath(path.join(self.current_dir, self.str_path))
                for vendor in self.vendors:
                    base_dir = re.split(vendor,file_path)
                    dest_file_path = base_dir[0] + complete_path
                    if path.isfile(dest_file_path):
                        return dest_file_path
        return ''

    def is_valid_line(self, line_content):
        for regex_str in dirs_regex:
            pattern = re.compile(regex_str)
            matched = pattern.match(line_content)
            if matched:
                return matched
        return False
