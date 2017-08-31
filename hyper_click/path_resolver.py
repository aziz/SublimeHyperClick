# -*- coding: utf-8 -*-
from os import path
from .js_path_resolver import JsPathResolver
from .sass_path_resolver import SassPathResolver
from .less_path_resolver import LessPathResolver
from .php_path_resolver import PhpPathResolver
from .html_path_resolver import HTMLPathResolver
from .path_generic_subfolder_resolver import GenericSubfolderResolver


class HyperClickPathResolver:
    def __init__(self, str_path, current_file, roots, lang, settings):
        current_dir = path.dirname(path.realpath(current_file))
        if lang == 'js':
            self.resolver = JsPathResolver(str_path, current_dir, roots, lang, settings)
        elif lang == 'sass':
            self.resolver = SassPathResolver(str_path, current_dir, roots, lang, settings)
        elif lang == 'less':
            self.resolver = LessPathResolver(str_path, current_dir, roots, lang, settings)
        elif lang == 'php':
            self.resolver = PhpPathResolver(str_path, current_dir, roots, lang, settings)
        elif lang == 'html':
            self.resolver = HTMLPathResolver(str_path, current_dir, roots, lang, settings)
        else:
            self.resolver = GenericSubfolderResolver(str_path, current_dir, roots, lang, settings)

    def resolve(self):
        return self.resolver.resolve()
