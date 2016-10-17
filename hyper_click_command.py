# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import re
from . import hyper_click as HC


class HyperClickJumpCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.current_line = (-1, -1)
        self.view = view
        self.settings = sublime.load_settings('hyper_click.sublime-settings')
        self.window = view.window()
        self.roots = view.window().folders()
        self.syntax = self.view.settings().get('syntax')
        self.lang = self.get_lang(self.syntax)

    def run(self, edit):
        v = self.view

        if len(v.sel()) != 1:
            return

        cursor = v.sel()[0].a
        line_range = v.line(cursor)
        line_content = v.substr(line_range).strip()
        matched = self.is_valid_line(line_content)
        if matched:
            destination_str = matched.group(1)
            file_path = HC.HyperClickPathResolver(
                destination_str, v.file_name(),
                self.roots, self.lang, self.settings
            )
            if len(file_path.resolve()) > 0:
                self.window.open_file(file_path.resolve())

    def is_valid_line(self, line_content):
        import_lines = self.settings.get('import_line_regex', {})
        for regex_str in import_lines[self.lang]:
            pattern = re.compile(regex_str)
            matched = pattern.match(line_content)
            if matched:
                return matched
        return False

    def get_lang(self, syntax):
        supported_syntaxes = self.settings.get('supported_syntaxes')
        for (lang, syntax_names) in supported_syntaxes.items():
            for syn in syntax_names:
                if self.syntax.endswith(syn):
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
        return self.is_enabled()
