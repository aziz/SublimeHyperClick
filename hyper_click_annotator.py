import sublime_plugin
import sublime
import re
import webbrowser
from itertools import chain
from .hyper_click.path_resolver import HyperClickPathResolver


def is_applicable(scope, view):
    if int(sublime.version()) < 3118:
        # phantoms are not supported
        return False

    if not scope:
        return False

    settins = sublime.load_settings('hyper_click.sublime-settings')
    annotations_enabled = settins.get('annotations_enabled')
    if not annotations_enabled:
        return False

    selector = settins.get('selector')
    if view.match_selector(view.sel()[0].a, selector):
        return True

    return False


class HyperClickAnnotator(sublime_plugin.EventListener):

    def __init__(self):
        self.current_line = (-1, -1)

    def is_valid_line(self, line_content, view):
        settings = sublime.load_settings('hyper_click.sublime-settings')
        scopes = settings.get('scopes', {})
        for selector in scopes:
            if view.match_selector(view.sel()[0].a, selector):
                for regex_str in scopes[selector]['regexes']:
                    pattern = re.compile(regex_str)
                    matched = pattern.match(line_content)
                    if matched:
                        return matched
        return False

    def on_navigate(self, url):
        if url.startswith('http://') or url.startswith('https://'):
            webbrowser.open_new_tab(url)
        else:
            self.window.open_file(url)

    def annotate(self, point, view):
        self.window = view.window()
        self.roots = view.window().folders()
        self.syntax = view.settings().get('syntax')
        settings = sublime.load_settings('hyper_click.sublime-settings')

        # Per-project settings are optional
        self.proj_settings = view.settings().get('hyper_click', {})

        line_range = view.line(point)

        if view.line(line_range.b) == self.current_line:
            return

        line_content = view.substr(line_range).strip()
        matched = self.is_valid_line(line_content, view)

        if matched:
            CSS = sublime.load_resource("Packages/HyperClick/html/ui.css")
            HTML = sublime.load_resource("Packages/HyperClick/html/ui.html")
            destination_str = matched.group(1)
            file_path = HyperClickPathResolver(
                view,
                destination_str,
                self.roots,
                settings
            )
            region = sublime.Region(line_range.b, line_range.b)
            self.current_line = view.line(line_range.b)
            view.erase_phantoms('hyper_click')
            resolved_path = file_path.resolve()
            if resolved_path:
                content = """
                    <span class="label label-success"><a href="{link}">{content}</a></span>
                """.format(
                    link=resolved_path,
                    content=settings.get('annotation_found_text', '➜')
                )
                view.add_phantom(
                    'hyper_click',
                    region,
                    HTML.format(css=CSS, content=content),
                    sublime.LAYOUT_INLINE, self.on_navigate
                )
            else:
                content = """
                    <span class="label label-error">{content}</span>
                """.format(content=settings.get('annotation_not_found_text', '✘'))
                view.add_phantom(
                    'hyper_click',
                    region,
                    HTML.format(css=CSS, content=content),
                    sublime.LAYOUT_INLINE, self.on_navigate
                )
        else:
            self.current_line = (-1, -1)
            view.erase_phantoms('hyper_click')

    # ---------------------------------------

    def on_selection_modified_async(self, view):
        if view.is_dirty():
            view.erase_phantoms('hyper_click')
            return

        if len(view.sel()) != 1:
            view.erase_phantoms('hyper_click')
            return

        point = view.sel()[0].a
        self.annotate(point, view)

    def on_activated_async(self, view):
        self.on_selection_modified_async(view)

    def on_deactivated_async(self, view):
        view.erase_phantoms('hyper_click')

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'hyper_click_jump_line':
            cursor = view.sel()[0].a
            line_range = view.line(cursor)
            line_content = view.substr(line_range).strip()
            return bool(self.is_valid_line(line_content))
        return None

    def on_hover(self, view, point, hover_zone):
        self.annotate(point, view)
