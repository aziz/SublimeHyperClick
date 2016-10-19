# -*- coding: utf-8 -*-
import json
from os import path


class JsPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        self.default_filenames = settings.get('default_filenames', {})[lang]
        self.vendor_dirs = settings.get('vendor_dirs', {})[lang]

    def resolve(self):
        if self.str_path.startswith('.'):
            return self.resolve_relative_path()
        else:
            if '/' in self.str_path:
                return self.resolve_package_internal_path()
            else:
                return self.resolve_package_root_path()

    def resolve_relative_path(self):
        combined = path.realpath(path.join(self.current_dir, self.str_path))
        # matching ../index to /index.js
        for ext in self.valid_extensions:
            file_path = combined + '.' + ext
            if path.isfile(file_path):
                return file_path

        # matching ./demo to /demo/index.js
        if path.isdir(combined):
            for default_name in self.default_filenames:
                for ext in self.valid_extensions:
                    file_path = path.join(combined, default_name + '.' + ext)
                    if path.isfile(file_path):
                        return file_path
        return ''

    def resolve_package_root_path(self):
        for root in self.roots:
            for vendor_dir in self.vendor_dirs:
                combined = path.realpath(path.join(root, vendor_dir, self.str_path))
                package_json_path = path.join(combined, 'package.json')
                if path.isdir(combined) and path.isfile(package_json_path):
                    with open(package_json_path, 'r', encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    return path.realpath(path.join(combined, data['main']))
        return ''

    def resolve_package_internal_path(self):
        for root in self.roots:
            for vendor_dir in self.vendor_dirs:
                combined = path.realpath(path.join(root, vendor_dir, self.str_path))

                for ext in self.valid_extensions:
                    file_path = combined + '.' + ext
                    if path.isfile(file_path):
                        return file_path

                if path.isdir(combined):
                    for default_name in self.default_filenames:
                        for ext in self.valid_extensions:
                            file_path = path.join(combined, default_name + '.' + ext)
                            if path.isfile(file_path):
                                return file_path
        return ''
