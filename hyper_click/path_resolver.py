# -*- coding: utf-8 -*-
from os import path
from .js_path_resolver import JsPathResolver
from .sass_path_resolver import SassPathResolver


class HyperClickPathResolver:
    def __init__(self, str_path, current_file, roots, lang, settings):
        current_dir = path.dirname(path.realpath(current_file))
        if lang == 'js':
            self.resolver = JsPathResolver(str_path, current_dir, roots, lang, settings)
        if lang == 'sass':
            self.resolver = SassPathResolver(str_path, current_dir, roots, lang, settings)

    def resolve(self):
        return self.resolver.resolve()
