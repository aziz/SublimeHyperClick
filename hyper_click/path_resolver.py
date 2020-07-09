from os import path
from .js_path_resolver import JsPathResolver
from .sass_path_resolver import SassPathResolver
from .jstl_path_resolver import JstlPathResolver
from .generic_path_resolver import GenericPathResolver


class HyperClickPathResolver:
    def __init__(self, view, str_path, roots, settings):
        current_file = view.file_name()
        current_dir = path.dirname(path.realpath(current_file))
        # if scope == 'source.js':
        #     self.resolver = JsPathResolver(view, str_path, current_dir, roots, settings, proj_settings)
        # elif scope == 'source.sass':
        #     self.resolver = SassPathResolver(view, str_path, current_dir, roots, settings, proj_settings)
        # elif scope == 'source.jstl':
        #     self.resolver = JstlPathResolver(view, str_path, current_dir, roots, settings)
        # else:
        self.resolver = GenericPathResolver(view, str_path, current_dir, roots, settings)

    def resolve(self):
        return self.resolver.resolve()
