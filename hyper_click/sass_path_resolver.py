# -*- coding: utf-8 -*-
from os import path


class SassPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings, proj_settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        self.proj_settings = proj_settings

        self.aliases = settings.get('aliases', {}).get(lang, {})
        self.proj_aliases = proj_settings.get('aliases', {}).get(lang, {})
        for alias in self.proj_aliases:
            self.aliases[alias] = self.proj_aliases[alias]

        self.matchingRoots = [root for root in self.roots if self.current_dir.startswith(root)]
        self.currentRoot = self.matchingRoots[0] if self.matchingRoots else self.current_dir
        self.lookup_paths = self.proj_settings.get('lookup_paths', {}).get(lang, False) or settings.get('lookup_paths', {}).get(lang, False) or []

    def resolve(self):
        for alias, alias_source in self.aliases.items():
            result = self.resolve_from_alias(alias, alias_source)
            if result:
                return result

        result = self.resolve_relative_to_dir(self.str_path, self.current_dir)
        if result:
            return result

        result = self.resolve_in_lookup_paths(self.str_path)
        if result:
            return result

        return ''

    def resolve_from_alias(self, alias, alias_source):
        alias_path = path.join(alias_source, self.str_path[len(alias) + 1:])
        result = self.resolve_relative_to_dir(alias_path, self.currentRoot)
        if result:
            return result

    def resolve_relative_to_dir(self, target, directory):
        combined = path.realpath(path.join(directory, target))
        return self.resolve_as_file(combined)

    def resolve_in_lookup_paths(self, target):
        for lookup_path in self.lookup_paths:
            result = self.resolve_relative_to_dir(target, path.join(self.currentRoot, lookup_path))
            if result:
                return result

    def resolve_as_file(self, path_name):
        # matching ../variables/palette to ../variables/palette.scss
        combined = path_name
        for ext in self.valid_extensions:
            file_path = combined + '.' + ext
            if path.isfile(file_path):
                return file_path

        # matching ../variables/palette to ../variables/_palette.scss
        pathname, filename = path.split(path_name)
        combined = path.join(pathname, '_' + filename)
        for ext in self.valid_extensions:
            file_path = combined + '.' + ext
            if path.isfile(file_path):
                return file_path
