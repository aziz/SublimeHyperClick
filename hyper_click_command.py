import sublime_plugin
import sublime
import re
from .hyper_click.path_resolver import HyperClickPathResolver
import webbrowser


def get_cursor(view, event=None):
    if event:
        vector = (event['x'], event['y'])
        point = view.window_to_text(vector)
        return sublime.Region(point)
    else:
        return view.sel()[0]


class HyperClickJumpCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.current_line = (-1, -1)
        self.view = view
        self.settings = sublime.load_settings('HyperClick.sublime-settings')
        self.window = view.window()

    def want_event(self):
        return True

    def run(self, edit, event=None):
        self.window = self.view.window()
        view = self.view

        if len(view.sel()) != 1:
            return

        # Setting self.roots here (instead of in `__init__`) fixes a bug with files opened through the quick panel
        self.roots = self.window and self.window.folders()

        cursor = get_cursor(view, event).a
        line_range = view.line(cursor)
        line_content = view.substr(line_range).strip()
        matched = self.is_valid_line(line_content)
        if matched:
            destination_str = matched.group(1)
            file_path = HyperClickPathResolver(
                view,
                destination_str,
                self.roots,
                self.settings
            )
            resolved_path = file_path.resolve()
            if resolved_path:
                if resolved_path.startswith('http://') or resolved_path.startswith('https://'):
                    webbrowser.open_new_tab(resolved_path)
                else:
                    self.window.open_file(resolved_path)
                return

        self.window.status_message("File not found")

    def is_valid_line(self, line_content):
        view = self.view
        scopes = self.settings.get('scopes', {})
        for selector in scopes:
            if view.match_selector(view.sel()[0].a, selector):
                for regex_str in scopes[selector]['regexes']:
                    pattern = re.compile(regex_str)
                    matched = pattern.match(line_content)
                    if matched:
                        return matched
        return False

    def is_visible(self, event=None):
        view = self.view
        selector = self.settings.get('selector')
        if not view.match_selector(view.sel()[0].a, selector):
            return False
        else:
            cursor = get_cursor(view, event)
            if not (len(view.sel()) == 1 and cursor.empty()):
                return False

            line_range = view.line(cursor)
            line_content = view.substr(line_range).strip()
            matched = self.is_valid_line(line_content)
            if matched:
                return True
            return False
