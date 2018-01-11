# -*- coding: utf-8 -*-
from os import path
from .js_path_resolver import JsPathResolver
from .sass_path_resolver import SassPathResolver
from .jstl_path_resolver import JstlPathResolver
from .path_generic_resolver import GenericPathResolver


class HyperClickPathResolver:
    def __init__(self, view, str_path, roots, lang, settings,
        proj_settings):
        current_file = view.file_name()
        current_dir = path.dirname(path.realpath(current_file))
        if lang == 'js':
            self.resolver = JsPathResolver(str_path, current_dir, roots, lang, settings, proj_settings)
        elif lang == 'sass':
            self.resolver = SassPathResolver(str_path, current_dir, roots, lang, settings, proj_settings)
        elif lang == 'jstl':
            self.resolver = JstlPathResolver(view, str_path, current_dir, roots, lang, settings)
        else:
            self.resolver = GenericPathResolver(str_path, current_dir, roots, lang, settings, proj_settings)

    def resolve(self):
        return self.resolver.resolve()
