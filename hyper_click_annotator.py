# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import re
from itertools import chain
from . import hyper_click as HC

ST3118 = int(sublime.version()) >= 3118

if ST3118:
    class HyperClickAnnotator(sublime_plugin.ViewEventListener):
        @classmethod
        def is_applicable(cls, settings):
            syntax = settings.get('syntax')
            plugin_settings = sublime.load_settings('hyper_click.sublime-settings')
            annotations_enabled = plugin_settings.get('annotations_enabled')
            if not annotations_enabled:
                return False
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
            self.lang = self.get_lang(self.syntax)

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

        def on_navigate(self, url):
            self.window.open_file(url)

        def on_selection_modified_async(self):
            v = self.view

            if v.is_dirty():
                v.erase_phantoms('hyper_click')
                return

            if len(v.sel()) != 1:
                v.erase_phantoms('hyper_click')
                return

            cursor = v.sel()[0].a
            line_range = v.line(cursor)

            if v.line(line_range.b) == self.current_line:
                return

            line_content = v.substr(line_range).strip()
            matched = self.is_valid_line(line_content)

            if matched:
                destination_str = matched.group(1)
                file_path = HC.HyperClickPathResolver(
                    destination_str, v.file_name(),
                    self.roots, self.lang, self.settings
                )
                region = sublime.Region(line_range.b, line_range.b)
                self.current_line = v.line(line_range.b)
                v.erase_phantoms('hyper_click')
                if len(file_path.resolve()) > 0:
                    content = """
                        <span class="label label-success"><a href="{link}">{content}</a></span>
                    """.format(link=file_path.resolve(), content=self.settings.get('annotation_found_text', '➜'))
                    v.add_phantom(
                        'hyper_click',
                        region,
                        self.html.format(css=self.css, content=content),
                        sublime.LAYOUT_INLINE, self.on_navigate
                    )
                else:
                    content = """
                        <span class="label label-error">{content}</span>
                    """.format(content=self.settings.get('annotation_not_found_text', '✘'))
                    v.add_phantom(
                        'hyper_click',
                        region,
                        self.html.format(css=self.css, content=content),
                        sublime.LAYOUT_INLINE, self.on_navigate
                    )
            else:
                v.erase_phantoms('hyper_click')

        def on_activated_async(self):
            self.on_selection_modified_async()

        def on_deactivated_async(self):
            self.view.erase_phantoms('hyper_click')

        def on_query_context(self, key, operator, operand, match_all):
            if key == 'hyper_click_jump_line':
                v = self.view
                cursor = v.sel()[0].a
                line_range = v.line(cursor)
                line_content = v.substr(line_range).strip()
                if self.is_valid_line(line_content):
                    return True
                else:
                    return False

            return None
