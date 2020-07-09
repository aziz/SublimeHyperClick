import sublime
from os import path


# A default resolver that resolves to a subfolder along along with one of the valid extensions
class GenericPathResolver:
    def __init__(self, view, str_path, current_dir, roots, settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.aliases = []
        self.valid_extensions = []
        self.lookup_paths = []

        matching_roots = [root for root in roots if self.current_dir.startswith(root)]
        self.current_root = matching_roots[0] if matching_roots else self.current_dir

        scopes = settings.get('scopes', {})
        for selector in scopes:
            if view.match_selector(view.sel()[0].a, selector):
                self.aliases = scopes[selector].get('aliases', [])
                self.valid_extensions = scopes[selector].get('extensions', [])
                self.lookup_paths = scopes[selector].get('lookup_paths', [])

        # check the view for applicable project settings
        project_settings = view.settings().get('hyper_click', {})
        project_scopes = project_settings.get('scopes', {})
        for selector in project_scopes:
            if view.match_selector(view.sel()[0].a, selector):
                self.aliases.extend(
                    project_scopes[selector].get('aliases', [])
                )
                self.valid_extensions.extend(
                    project_scopes[selector].get('extensions', [])
                )
                self.lookup_paths.extend(
                    project_scopes[selector].get('lookup_paths', [])
                )

    def resolve(self):
        combined = path.realpath(path.join(self.current_dir, self.str_path))

        # Try to match the literal filename referenced
        # match: '../variables/palette.less'
        if path.isfile(combined):
            return combined

        # Try to use the path given in project settings for this language
        result = self.resolve_in_lookup_paths(self.str_path)
        if result:
            return result

        # Resolve by alias
        # match 'Styles/variables/palette' to 'src/less/variables/palette.less'
        # for alias, alias_source in self.aliases.items():
        #     result = self.resolve_from_alias(alias, alias_source)
        #     if result:
        #         return result

        return ''

    def resolve_relative_to_dir(self, target, directory):
        combined = path.realpath(path.join(directory, target))
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

    def resolve_as_file(self, path_name):
        if path.isfile(path_name):
            return path_name

        # matching ../index to /index.js
        for ext in self.valid_extensions:
            file_path = path_name + '.' + ext
            if path.isfile(file_path):
                return file_path
