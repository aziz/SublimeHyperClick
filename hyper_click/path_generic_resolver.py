# -*- coding: utf-8 -*-
from os import path


# A default resolver that resolves to a subfolder along along with one of the valid extensions
class GenericPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings, proj_settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        self.proj_settings = proj_settings

        self.matching_root = [root for root in self.roots if self.current_dir.startswith(root)]
        self.current_root = self.matching_root[0]
        self.lookup_paths = self.proj_settings.get('lookup_paths', {}).get(lang, False) or settings.get('lookup_paths', {}).get(lang, False) or []

    def resolve(self):
        combined = path.realpath(path.join(self.current_dir, self.str_path))

        # Try to match the literal filename referenced
        # match: '../variables/palette.less'
        if path.isfile(combined):
            return combined

        # Try to use the path given in project settings for this language
        result = self.resolve_in_lookup_paths(self.str_path)
        if result:
            return result

        # Loop all allowed extensions, and try matching those
        # match '../variables/palette' to '../variables/palette.less'
        for ext in self.valid_extensions:
            file_path = combined + '.' + ext
            if path.isfile(file_path):
                return file_path

        return ''

    def resolve_relative_to_dir(self, target, directory):
        combined = path.realpath(path.join(directory, target))
        return self.resolve_as_file(combined)

    def resolve_in_lookup_paths(self, target):
        for lookup_path in self.lookup_paths:
            result = self.resolve_relative_to_dir(target, path.join(self.current_root, lookup_path))
            if result:
                return result

    def resolve_as_file(self, path_name):
        if path.isfile(path_name):
            return path_name
        # match imports without extension
        for ext in self.valid_extensions:
            file_path = path_name + '.' + ext
            if path.isfile(file_path):
                return file_path
