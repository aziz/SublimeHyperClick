# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import re
import webbrowser
from itertools import chain
from .hyper_click.path_resolver import HyperClickPathResolver

ST3118 = int(sublime.version()) >= 3118

if ST3118:
    class HyperClickAnnotator(sublime_plugin.ViewEventListener):
        @classmethod
        def is_applicable(cls, settings):
            syntax = settings.get('syntax', None)
            if not syntax:
                return False
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
            if url.startswith('http://') or url.startswith('https://'):
                webbrowser.open_new_tab(url)
            else:
                self.window.open_file(url)

        def annotate(self, point):
            self.window = self.view.window()
            self.roots = self.view.window().folders()
            self.syntax = self.view.settings().get('syntax')
            self.lang = self.get_lang(self.syntax)
            v = self.view
            line_range = v.line(point)

            if v.line(line_range.b) == self.current_line:
                return

            line_content = v.substr(line_range).strip()
            matched = self.is_valid_line(line_content)

            if matched:
                file_path = HyperClickPathResolver(v,
                    matched, v.file_name(),
                    self.roots, self.lang, self.settings
                )
                region = sublime.Region(line_range.b, line_range.b)
                self.current_line = v.line(line_range.b)
                v.erase_phantoms('hyper_click')
                resolved_path = file_path.resolve()
                # print('resolved to => ', resolved_path)
                if resolved_path:
                    content = """
                        <span class="label label-success"><a href="{link}">{content}</a></span>
                    """.format(
                        link=resolved_path,
                        content=self.settings.get('annotation_found_text', '➜')
                    )
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

        # ---------------------------------------

        def on_selection_modified_async(self):
            v = self.view

            if v.is_dirty():
                v.erase_phantoms('hyper_click')
                return

            if len(v.sel()) != 1:
                v.erase_phantoms('hyper_click')
                return

            point = v.sel()[0].a
            self.annotate(point)

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
                return bool(self.is_valid_line(line_content))
            return None

        def on_hover(self, point, hover_zone):
            self.annotate(point)
