# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import re
import json
from os import path
from itertools import chain


class HyperClickAnnotator(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        plugin_settings = sublime.load_settings('hyper_click.sublime-settings')
        supported_syntaxes = plugin_settings.get('supported_syntaxes')
        aggregated_systaxes = list(chain.from_iterable(supported_syntaxes.values()))
        for s in aggregated_systaxes:
            if syntax.endswith(s):
                return True
        return False

    def __init__(self, view):
        self.current_line = (-1, -1)
        self.view = view
        self.settings = sublime.load_settings('hyper_click.sublime-settings')
        self.css = sublime.load_resource("Packages/HyperClick/html/ui.css")
        self.html = sublime.load_resource("Packages/HyperClick/html/ui.html")
        self.window = view.window()
        self.roots = view.window().folders()
        self.syntax = self.view.settings().get('syntax')
        self.lang = self._get_lang(self.syntax)

    def is_valid_line(self, line_content):
        import_lines = self.settings.get('import_line_regex', {})
        for regex_str in import_lines[self.lang]:
            pattern = re.compile(regex_str)
            matched = pattern.match(line_content)
            if matched:
                return matched
        return False

    def _get_lang(self, syntax):
        supported_syntaxes = self.settings.get('supported_syntaxes')
        for (lang, syntax_names) in supported_syntaxes.items():
            for syn in syntax_names:
                if self.syntax.endswith(syn):
                    return lang
        return ''

    def on_navigate(self, url):
        self.window.open_file(url, sublime.ENCODED_POSITION)

    def on_selection_modified_async(self):
        v = self.view

        if v.is_dirty():
            v.erase_phantoms('hyper_click')
            return

        if not (len(v.sel()) == 1 and v.sel()[0].empty()):
            v.erase_phantoms('hyper_click')
            return

        cursor = v.sel()[0]
        line_range = v.line(cursor)

        if v.line(line_range.b) == self.current_line:
            return

        line_content = v.substr(line_range).strip()
        matched = self.is_valid_line(line_content)

        if matched:
            destination_str = matched.group(1)
            file_path = HyperClickPathResolver(
                destination_str, v.file_name(),
                self.roots, self.lang, self.settings
            )
            if len(file_path.resolve()) > 0:
                region = sublime.Region(line_range.b, line_range.b)
                self.current_line = v.line(line_range.b)
                v.erase_phantoms('hyper_click')
                content = """
                    <span class="label label-success"><a href="{}">➜</a></span>
                """.format(file_path.resolve())
                v.add_phantom(
                    'hyper_click',
                    region,
                    self.html.format(css=self.css, content=content),
                    sublime.LAYOUT_INLINE, self.on_navigate
                )
            else:
                v.erase_phantoms('hyper_click')
        else:
            v.erase_phantoms('hyper_click')


class HyperClickPathResolver:
    def __init__(self, str_path, current_file, roots, lang, settings):
        current_dir = path.dirname(path.realpath(current_file))
        if lang == 'js':
            self.resolver = JsPathResolver(str_path, current_dir, roots, lang, settings)

    def resolve(self):
        return self.resolver.resolve()


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
            return self.resolve_package_path()

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

    def resolve_package_path(self):
        for root in self.roots:
            for vendor_dir in self.vendor_dirs:
                combined = path.realpath(path.join(root, vendor_dir, self.str_path))
                package_json_path = path.join(combined, 'package.json')
                if path.isdir(combined) and path.isfile(package_json_path):
                    with open(package_json_path) as data_file:
                        data = json.load(data_file)
                    return path.realpath(path.join(combined, data['main']))
