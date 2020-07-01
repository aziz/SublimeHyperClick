# -*- coding: utf-8 -*-
from os import path


class SassPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings, proj_settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        proj_aliases = proj_settings.get('aliases', {}).get(lang, {})
        self.aliases = settings.get('aliases', {}).get(lang, {})
        self.aliases.update(proj_aliases)
        matching_roots = [root for root in roots if self.current_dir.startswith(root)]
        self.current_root = matching_roots[0] if matching_roots else self.current_dir
        self.lookup_paths = proj_settings.get('lookup_paths', {}).get(lang, []) + settings.get('lookup_paths', {}).get(lang, [])

    def resolve(self):
        result = self.resolve_relative_to_dir(self.str_path, self.current_dir)
        if result:
            return result

        for alias, alias_source in self.aliases.items():
            result = self.resolve_from_alias(alias, alias_source)
            if result:
                return result

        result = self.resolve_in_lookup_paths(self.str_path)
        if result:
            return result

        return ''

    def resolve_from_alias(self, alias, alias_source):
        path_parts = path.normpath(self.str_path).split(path.sep)

        if path_parts[0] == alias:
            path_parts[0] = alias_source

            return self.resolve_relative_to_dir(path.join(*path_parts), self.current_root)

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
        # matching ../variables/palette to ../variables/palette.scss
        for ext in self.valid_extensions:
            file_path = path_name + '.' + ext
            if path.isfile(file_path):
                return file_path

        # matching ../variables/palette to ../variables/_palette.scss
        pathname, filename = path.split(path_name)
        combined = path.join(pathname, '_' + filename)
        for ext in self.valid_extensions:
            file_path = combined + '.' + ext
            if path.isfile(file_path):
                return file_path
