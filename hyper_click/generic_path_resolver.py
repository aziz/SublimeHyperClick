from os import path
import json
import array
import sublime


NODE_CORE_MODULES = {'assert', 'async_hooks', 'buffer', 'child_process', 'cluster', 'console', 'constants', 'crypto', 'dgram', 'dns', 'domain', 'events', 'fs', 'http', 'http2', 'https', 'module', 'net', 'os', 'path', 'perf_hooks', 'process', 'punycode', 'querystring', 'readline', 'repl', 'stream', 'string_decoder', 'sys', 'timers', 'tls', 'trace_events', 'tty', 'url', 'util', 'v8', 'vm', 'wasi', 'worker_threads', 'zlib', 'assert/strict', 'dns/promises', 'fs/promises', 'stream/promises', 'timers/promises'}
NODE_CORE_MODULES_TEMPLATE = "https://github.com/nodejs/node/blob/master/lib/{}.js"

SASS_CORE_MODULES = {'sass:color', 'sass:list', 'sass:map', 'sass:math', 'sass:meta', 'sass:selector', 'sass:string'}
SASS_CORE_MODULES_TEMPLATE = "https://sass-lang.com/documentation/modules/{}"

def deep_get(d, keys, default=None):
    assert type(keys) is list
    if d is None:
        return default
    if not keys:
        return d
    return deep_get(d.get(keys[0]), keys[1:], default)

def find(lst, fn):
    return next((x for x in lst if fn(x)), None)

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


class GenericPathResolver:
    def __init__(self, view, str_path, current_dir, roots, settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.aliases = {}
        self.valid_extensions = []
        self.vendor_dirs = []
        self.lookup_paths = []

        cursor = view.sel()[0].b
        self.scope_is_js = view.match_selector(cursor, 'source.js,source.ts,source.jsx,source.tsx')
        self.scope_is_sass = view.match_selector(cursor, 'source.scss,source.sass')
        self.scope_is_css = view.match_selector(cursor, 'source.css')

        matching_roots = [root for root in roots if self.current_dir.startswith(root)]
        self.current_root = matching_roots[0] if matching_roots else self.current_dir

        scopes = settings.get('scopes', {})
        for selector in scopes:
            if view.match_selector(cursor, selector):
                self.aliases = scopes[selector].get('aliases', {})
                self.valid_extensions = scopes[selector].get('extensions', [])
                self.vendor_dirs = scopes[selector].get('vendor_dirs', [])
                self.lookup_paths = scopes[selector].get('vendor_dirs', [])
                self.lookup_paths.extend(
                    scopes[selector].get('lookup_paths', [])
                )

        # check the view for applicable project settings
        project_settings = view.settings().get('HyperClick', {})
        project_scopes = project_settings.get('scopes', {})
        for selector in project_scopes:
            if view.match_selector(cursor, selector):
                self.aliases.update(
                    project_scopes[selector].get('aliases', {})
                )
                self.valid_extensions.extend(
                    project_scopes[selector].get('extensions', [])
                )
                self.lookup_paths.extend(
                    project_scopes[selector].get('lookup_paths', [])
                )

    def resolve(self):
        if self.scope_is_js:
            # Core modules
            if self.str_path in NODE_CORE_MODULES:
                return NODE_CORE_MODULES_TEMPLATE.format(self.str_path)

        if self.scope_is_sass:
            # Core modules
            if self.str_path in SASS_CORE_MODULES:
                return SASS_CORE_MODULES_TEMPLATE.format(self.str_path.replace('sass:', ''))

        combined = path.realpath(path.join(self.current_dir, self.str_path))

        # match: '../variables/palette' -> '../variables/palette.less'
        # match: '../variables/palette' -> '../variables/_palette.scss'
        result = self.resolve_as_file(combined)
        if result:
            return result


        # Try to use the path given in project settings for this language
        result = self.resolve_in_lookup_paths(self.str_path)
        if result:
            return result

        # Resolve by alias
        # match 'Styles/variables/palette' to 'src/less/variables/palette.less'
        for alias, alias_source in self.aliases.items():
            result = self.resolve_from_alias(alias, alias_source)
            if result:
                return result

        if self.scope_is_js:
            result = self.resolve_node_modules(self.str_path, self.current_dir)
            if result:
                return result

        return ''

    def resolve_relative_to_dir(self, target, directory):
        combined = path.realpath(path.join(directory, target))
        if self.scope_is_js:
            return self.resolve_as_file(combined) or self.resolve_as_directory(combined)
        else:
            return self.resolve_as_file(combined)

    def resolve_in_lookup_paths(self, target):
        for lookup_path in self.lookup_paths:
            result = self.resolve_relative_to_dir(target, path.join(self.current_root, lookup_path))
            if result:
                return result

    def resolve_from_alias(self, alias, alias_source):
        path_parts = path.normpath(self.str_path).split(path.sep)

        if path_parts[0] == alias:
            path_parts[0] = alias_source

            return self.resolve_relative_to_dir(path.join(*path_parts), self.current_root)

    def resolve_with_exts(self, path_name):
        # matching ../index to /index.js
        for ext in self.valid_extensions:
            file_path = path_name + '.' + ext
            if path.isfile(file_path):
                return file_path

    def resolve_as_file(self, path_name):
        if path.isfile(path_name):
            return path_name

        with_ext = self.resolve_with_exts(path_name) or self.resolve_with_exts(path.join(path_name, 'index'))
        if with_ext:
            return with_ext

        # "A partial is a Sass file named with a leading underscore [that] should not be generated into a CSS file" - https://sass-lang.com/guide
        if self.scope_is_sass:
            underscore_extd = self.resolve_with_underscore(path_name)
            if underscore_extd:
                return underscore_extd

    def resolve_with_underscore(self, path_name):
        pathname, filename = path.split(path_name)
        combined = path.join(pathname, '_' + filename)

        if path.isfile(combined):
            return combined

        return self.resolve_with_exts(combined)

    def resolve_node_modules(self, target, start_dir):
        for vendor_path in walkup_dir(start_dir, self.vendor_dirs, self.current_root):
            lookup_path = path.join(vendor_path, target)
            result = self.resolve_as_file(lookup_path)
            if result:
                return result
            result = self.resolve_as_directory(lookup_path)
            if result:
                return result

    def resolve_index(self, dirname):
        # matching ./demo to /demo/index.js
        if path.isdir(dirname):
            return self.resolve_as_file(path.join(dirname, 'index.js'))

    def resolve_as_directory(self, dirname):
        package_json_path = path.join(dirname, 'package.json')
        if path.isdir(dirname) and path.isfile(package_json_path):
            with open(package_json_path, 'r', encoding='utf-8') as data_file:
                data = json.load(data_file)

            main_file_sources = []
            exports_dict = data.get('exports', None)
            if exports_dict:
                if self.scope_is_sass:
                    main_file_sources.append(deep_get(data, ['exports', '.', 'sass']))
                if self.scope_is_sass or self.scope_is_css:
                    main_file_sources.append(deep_get(data, ['exports', '.', 'style']))
                main_file_sources.append(deep_get(data, ['exports', '.', 'import']))
                main_file_sources.append(deep_get(data, ['exports', '.', 'require']))
                main_file_sources.append(deep_get(data, ['exports', '.', 'node']))
                main_file_sources.append(deep_get(data, ['exports', '.', 'default']))
                if self.scope_is_sass:
                    main_file_sources.append(deep_get(data, ['exports', 'sass']))
                if self.scope_is_sass or self.scope_is_css:
                    main_file_sources.append(deep_get(data, ['exports', 'style']))
                main_file_sources.append(deep_get(data, ['exports', 'import']))
                main_file_sources.append(deep_get(data, ['exports', 'require']))
                main_file_sources.append(deep_get(data, ['exports', 'node']))
                main_file_sources.append(deep_get(data, ['exports', 'default']))
                main_file_sources.append(deep_get(data, ['exports', '.']))
                main_file_sources.append(deep_get(data, ['exports']))
            else:
                if self.scope_is_sass or self.scope_is_css:
                    main_file_sources.append(deep_get(data, ['style']))
                main_file_sources.append(deep_get(data, ['module']))
                main_file_sources.append(deep_get(data, ['main']))

            main_file = find(main_file_sources, lambda string: type(string) == str)

            if main_file:
                dest = path.realpath(path.join(dirname, main_file))
                result = self.resolve_nodepath(dest)
                if result:
                    return result
        return self.resolve_index(dirname)

    def resolve_nodepath(self, nodepath):
        return self.resolve_as_file(nodepath) or self.resolve_index(nodepath)
