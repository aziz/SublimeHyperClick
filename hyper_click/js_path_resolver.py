# -*- coding: utf-8 -*-
import json
from os import path, walk

NODE_CORE_MODULES = ["assert", "buffer", "child_process", "cluster", "console", "constants",
                     "crypto", "dgram", "dns", "domain", "events", "fs", "http", "https",
                     "module", "net", "os", "path", "process", "punycode", "querystring",
                     "readline", "repl", "stream", "string_decoder", "sys", "timers", "tls",
                     "tty", "url", "util", "v8", "vm", "zlib"]

NODE_CORE_MODULES_TEMPLATE = "https://github.com/nodejs/node/blob/master/lib/{}.js"


class JsPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        self.default_filenames = settings.get('default_filenames', {})[lang]
        self.vendors = settings.get('vendor_dirs', {})[lang]
        self.vendor_dirs = [];
        self.matchingRoot = [root for root in self.roots if self.current_dir.startswith(root)]

        start_path = self.current_dir
        for vendor in self.vendors:
            last_root    = start_path
            current_root = start_path
            found_path = None

            while found_path is None and current_root:
                pruned = False
                for root, dirs, files in walk(current_root):
                    if not pruned:
                       try:
                          # R'.emove the part of the tree we already searched
                          del dirs[dirs.index(path.basename(last_root))]
                          pruned = True
                       except ValueError:
                          pass
                    if vendor in dirs:
                       # found the vendor direcotry, stop
                       found_path = path.join(root, vendor)
                       self.vendor_dirs.append(found_path)
                       break
                # Otherwise, pop up a level, search again
                last_root    = current_root
                try:
                    current_root = [path.dirname(last_root) for root in self.roots if path.dirname(last_root).startswith(root)][0]
                except IndexError:
                    current_root = None


    def resolve(self):
        if self.str_path.startswith('.'):
            return self.resolve_relative_path()
        else:
            if '/' in self.str_path and not self.str_path.startswith('@'):
                return self.resolve_package_internal_path()
            else:
                return self.resolve_package_root_path()

    def resolve_relative_path(self):
        combined = path.realpath(path.join(self.current_dir, self.str_path))

        if path.isfile(combined):
            return combined

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
        for root in self.matchingRoot:
            for vendor_dir in self.vendor_dirs:
                combined = path.realpath(path.join(root, vendor_dir, self.str_path))
                package_json_path = path.join(combined, 'package.json')
                if path.isdir(combined) and path.isfile(package_json_path):
                    with open(package_json_path, 'r', encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    main_file = data.get('main', None)
                    if main_file:
                        dest = path.realpath(path.join(combined, data['main']))
                        if path.isfile(dest):
                            return path.realpath(path.join(combined, data['main']))
                        else:
                            for ext in self.valid_extensions:
                                if path.isfile(dest + '.' + ext):
                                    return dest + '.' + ext
                            for default_name in self.default_filenames:
                                for ext in self.valid_extensions:
                                    file_path = path.join(dest, default_name + '.' + ext)
                                    if path.isfile(file_path):
                                        return file_path
                    else:
                        for default_name in self.default_filenames:
                            for ext in self.valid_extensions:
                                file_path = path.join(combined, default_name + '.' + ext)
                                if path.isfile(file_path):
                                    return file_path

        # is it a node core module?
        if self.str_path in NODE_CORE_MODULES:
            return NODE_CORE_MODULES_TEMPLATE.format(self.str_path)

        return ''

    def resolve_package_internal_path(self):
        for root in self.roots:
            for vendor_dir in self.vendor_dirs:
                combined = path.realpath(path.join(root, vendor_dir, self.str_path))

                if path.isfile(combined):
                    return combined

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
