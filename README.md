# Sublime HyperClick
Quickly and easily jump between your files. The missing part of `Go to definition` functionality in Sublime.

![sublimehyperclick](https://cloud.githubusercontent.com/assets/3202/19578519/51558bb4-971c-11e6-8ef2-d256da53d1da.gif)


## Supported Languages and Syntaxes

|  Language  |                                                Syntax                                               |
|------------|-------------------------------------------------------------------------------------------------------|
| Javascript | `ecmascript.sublime-syntax` <br> `JavaScript.sublime-syntax` <br> `JavaScript (Babel).sublime-syntax` |
| Sass       | `SCSS.tmLanguage` <br> `Sass.tmLanguage`                                                              |

*You can contribute and add more languages by adding a path resolver like [SassPathResolver](https://github.com/aziz/SublimeHyperClick/blob/master/hyper_click/sass_path_resolver.py)*


## Installation
You can install via [Sublime Package Control]()

Or clone this repo into your SublimeText Packages directory and rename it to `HyperClick`

## Usage
* phantoms
    * on hover
    * on cursor line
* context menu
* shortcut key

<img width="748" alt="sublimehyperclickcontext" src="https://cloud.githubusercontent.com/assets/3202/19578923/480cacde-971e-11e6-9504-91c26737c486.png">

## Settings
- disable annotations
- change phantom contents

```json
{
  "supported_syntaxes": {
    "js": [
      "ecmascript.sublime-syntax",
      "JavaScript.sublime-syntax",
      "JavaScript (Babel).sublime-syntax"
    ],
    "sass": [
      "SCSS.tmLanguage",
      "Sass.tmLanguage"
    ]
  },
  "import_line_regex": {
    "js": [
      "^import\\s+.+\\s+from\\s+['\"](.+)['\"];?$",
      "^import\\s+['\"](.+)['\"];?$",
      ".+require\\(['\"](.+)['\"]\\).+"
    ],
    "sass": [
      "^@import\\s+['\"](.+)['\"];?$"
    ]
  },
  "valid_extensions": {
    "js": ["js", "jsx"],
    "sass": ["scss", "sass"]
  },
  "default_filenames": {
    "js": ["index"]
  },
  "vendor_dirs": {
    "js": ["node_modules"]
  },
  "annotation_found_text": "➜",
  "annotation_not_found_text": "✘",
  "annotations_enabled": true
}
```

## License
Copyright 2016 [Allen Bargi](https://twitter.com/aziz). Licensed under the MIT License
