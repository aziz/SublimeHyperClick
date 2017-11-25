# -*- coding: utf-8 -*-
from os import path


# A default resolver that resolves to a subfolder along along with one of the valid extensions
class GenericPathResolver:
    def __init__(self, str_path, current_dir, roots, lang, settings):
        self.str_path = str_path
        self.current_dir = current_dir
        self.lang = lang
        self.settings = settings
        self.roots = roots
        self.valid_extensions = settings.get('valid_extensions', {})[lang]

    def resolve(self):
        combined = path.realpath(path.join(self.current_dir, self.str_path))

        # Try to match the literal filename referenced
        # match: '../variables/palette.less'
        if path.isfile(combined):
            return combined

        # Loop all allowed extensions, and try matching those
        # match '../variables/palette' to '../variables/palette.less'
        for ext in self.valid_extensions:
            file_path = combined + '.' + ext
            if path.isfile(file_path):
                return file_path
        return ''

