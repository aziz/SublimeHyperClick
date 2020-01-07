# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import re
from .hyper_click.path_resolver import HyperClickPathResolver
import webbrowser


class HyperClickJumpCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.current_line = (-1, -1)
        self.view = view
        self.settings = sublime.load_settings('hyper_click.sublime-settings')
        self.window = view.window()
        self.syntax = self.view.settings().get('syntax')
        self.lang = self.get_lang(self.syntax)

    def run(self, edit):
        self.window = self.view.window()
        v = self.view

        if len(v.sel()) != 1:
            return

        # Setting self.roots here (instead of in `__init__`) fixes a bug with files opened through the quick panel
        self.roots = self.window and self.window.folders()
        # Per-project settings are optional
        self.proj_settings = self.view.settings().get('hyper_click', {})

        cursor = v.sel()[0].a
        line_range = v.line(cursor)
        line_content = v.substr(line_range).strip()
        matched = self.is_valid_line(line_content)
        if matched:
            destination_str = matched.group(1)
            file_path = HyperClickPathResolver(
                v, destination_str,
                self.roots, self.lang, self.settings,
                self.proj_settings
            )
            resolved_path = file_path.resolve()
            if resolved_path:
                if resolved_path.startswith('http://') or resolved_path.startswith('https://'):
                    webbrowser.open_new_tab(resolved_path)
                else:
                    self.window.open_file(resolved_path)

    def is_valid_line(self, line_content):
        import_lines = self.settings.get('import_line_regex', {})
        for regex_str in import_lines.get(self.lang, []):
            pattern = re.compile(regex_str)
            matched = pattern.match(line_content)
            if matched:
                return matched
        return False

    def get_lang(self, syntax):
        supported_syntaxes = self.settings.get('supported_syntaxes')
        for (lang, syntax_names) in supported_syntaxes.items():
            for syn in syntax_names:
                if self.syntax.endswith('/' + syn):
                    return lang
        return ''

    def is_enabled(self):
        v = self.view

        if not (len(v.sel()) == 1 and v.sel()[0].empty()):
            return False

        cursor = v.sel()[0]
        line_range = v.line(cursor)
        line_content = v.substr(line_range).strip()
        matched = self.is_valid_line(line_content)
        if matched:
            return True
        return False

    def is_visible(self):
        if len(self.lang) == 0:
            return False
        else:
            return self.is_enabled()
