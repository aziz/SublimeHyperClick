# -*- coding: utf-8 -*-
import json
from os import path, walk
from bisect import bisect_left

NODE_CORE_MODULES = sorted(["assert", "buffer", "child_process", "cluster", "console", "constants",
                     "crypto", "dgram", "dns", "domain", "events", "fs", "http", "https",
                     "module", "net", "os", "path", "process", "punycode", "querystring",
                     "readline", "repl", "stream", "string_decoder", "sys", "timers", "tls",
                     "tty", "url", "util", "v8", "vm", "zlib"])

NODE_CORE_MODULES_TEMPLATE = "https://github.com/nodejs/node/blob/master/lib/{}.js"

def find_index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    return -1

def walkup_dir(start_path, vendor_dirs, endpath = '/'):
    current_dir = start_path
    target = current_dir
    while True:
        for dirname in vendor_dirs:
            target = path.join(current_dir, dirname)
            if path.isdir(target):
                yield target
            if current_dir == endpath:
                return
            # go up
            parent_dir = path.dirname(current_dir)
            if len(parent_dir) == len(current_dir):
                return
            current_dir = parent_dir

# doc: https://nodejs.org/dist/latest-v8.x/docs/api/modules.html#modules_all_together

class JsPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings, proj_settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]
        self.proj_settings = proj_settings
        self.vendor_dirs = settings.get('vendor_dirs', {})[lang];
        self.aliases = settings.get('aliases',{})[lang]
        self.matchingRoots = [root for root in self.roots if self.current_dir.startswith(root)]
        self.currentRoot = self.matchingRoots[0] if self.matchingRoots else self.current_dir
        self.lookup_paths = self.proj_settings.get('lookup_paths', {}).get(lang, False) or settings.get('lookup_paths', {}).get(lang, False) or []

    def resolve(self):
        # Resolve by global aliases
        for alias, alias_source in self.aliases.items():
            result = self.resolve_from_alias(alias, alias_source)
            if result:
                return result

        # Core modules
        if find_index(NODE_CORE_MODULES, self.str_path) != -1:
            return NODE_CORE_MODULES_TEMPLATE.format(self.str_path)

        # Relative paths
        context_dir = self.current_dir
        if self.str_path.startswith('/'):
            context_dir = '/'

        if self.str_path.startswith('./') or self.str_path.startswith('../') or context_dir == '/':
            result = self.resolve_relative_to_dir(self.str_path, context_dir)
            if result:
                return result

        # Lookup paths
        result = self.resolve_in_lookup_paths(self.str_path)
        if result:
            return result

        # Node modules
        return self.resolve_node_modules(self.str_path, self.current_dir)

    def resolve_from_alias (self, alias, alias_source):
        alias_path = path.join(alias_source, self.str_path[len(alias) + 1:])
        result = self.resolve_relative_to_dir(alias_path, self.currentRoot)
        if result:
            return result
    
    def resolve_relative_to_dir(self, target, directory):
        combined = path.realpath(path.join(directory, target))
        return self.resolve_as_file(combined) or self.resolve_as_directory(combined)

    def resolve_node_modules(self, target, start_dir):
        for vendor_path in walkup_dir(start_dir, self.vendor_dirs, self.currentRoot):
            lookup_path = path.join(vendor_path, target)
            result = self.resolve_as_file(lookup_path)
            if result:
                return result
            result = self.resolve_as_directory(lookup_path)
            if result:
                return result

    def resolve_in_lookup_paths(self, target):
        for lookup_path in self.lookup_paths:
            result = self.resolve_relative_to_dir(target, path.join(self.currentRoot, lookup_path))
            if result:
                return result

    def resolve_as_file(self, path_name):
        if path.isfile(path_name):
            return path_name
        # matching ../index to /index.js
        for ext in self.valid_extensions:
            file_path = path_name + '.' + ext
            if path.isfile(file_path):
                return file_path

    def resolve_index(self, dirname):
        # matching ./demo to /demo/index.js
        if path.isdir(dirname):
            return self.resolve_as_file(path.join(dirname, 'index'))

    def resolve_as_directory(self, dirname):
        package_json_path = path.join(dirname, 'package.json')
        if path.isdir(dirname) and path.isfile(package_json_path):
            with open(package_json_path, 'r', encoding='utf-8') as data_file:
                data = json.load(data_file)
            main_file = data.get('main', None)
            if main_file:
                dest = path.realpath(path.join(dirname, data['main']))
                result = self.resolve_nodepath(dest)
                if result:
                    return result
        return self.resolve_index(dirname)

    def resolve_nodepath(self, nodepath):
        return self.resolve_as_file(nodepath) or self.resolve_index(nodepath)


