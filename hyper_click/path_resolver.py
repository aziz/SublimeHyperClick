from os import path
from .jstl_path_resolver import JstlPathResolver
from .generic_path_resolver import GenericPathResolver


class HyperClickPathResolver:
    def __init__(self, view, str_path, roots, settings):
        current_file = view.file_name()
        current_dir = path.dirname(path.realpath(current_file))

        if view.match_selector(view.sel()[0].a, 'text.html.jstl'):
            self.resolver = JstlPathResolver(view, str_path, current_dir, roots, settings)
        else:
            self.resolver = GenericPathResolver(view, str_path, current_dir, roots, settings)

    def resolve(self):
        return self.resolver.resolve()
