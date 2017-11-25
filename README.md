# Sublime HyperClick
Quickly and easily jump between your files.
The missing part of `Go to definition` functionality in Sublime.

![sublime hyperclick](https://cloud.githubusercontent.com/assets/3202/19578519/51558bb4-971c-11e6-8ef2-d256da53d1da.gif)

Most of the time when you are navigating and reading a code-base, you need to
jump between required/imported (whatever jargon your programming language uses)
files. `Go to Definition` functionality of Sublime, trying to be a generic solution,
falls short for most languages since jumping between these required files needs
some knowledge about how the language or package manager of the language is working.

HyperClick tries to solve this issue. Currently, it knows how to jump between files in the following languages, but it can easily be extended to add more languages:

## Supported Languages and Syntaxes

|  Language  |  Syntax                                  |
|------------|------------------------------------------|
| Javascript | `ecmascript.sublime-syntax` <br> `JavaScript.sublime-syntax` <br> `JavaScript (Babel).sublime-syntax` <br> `JavaScriptNext.tmLanguage` |
| Sass       | `SCSS.tmLanguage` <br> `Sass.tmLanguage` |
| Less       | `LESS.tmLanguage`                        |
| Stylus     | `Stylus.tmLanguage`                      |
| PHP        | `PHP.sublime-syntax` <br> `PHP Source.sublime-syntax`  |
| HTML       | `HTML.sublime-syntax` |
| JSTL       | `JSTL.sublime-syntax` |
| CSS/PostCSS | `CSS.sublime-syntax` <br> `PostCSS.tmLanguage` |
| Pug        | `Pug.tmLanguage` |
| SugarSS    | `Sss.tmLanguage` <br> `SugarSS.tmLanguage` |
| SugarML    | `SugarML.tmLanguage` |
| Nunjucks   | `Nunjucks.tmLanguage` |
| Jinja2     | `Jinja2.tmLanguage` |
| Twig       | `HTML (Twig).tmLanguage` <br> `Craft-Twig.tmLanguage` |

*You can contribute and add more languages by adding a path resolver like [SassPathResolver](https://github.com/aziz/SublimeHyperClick/blob/master/hyper_click/sass_path_resolver.py)*


## Installation
You can install HyperClick via [Sublime Package Control](https://packagecontrol.io/)

Or clone this repo into your SublimeText Packages directory and rename it to `HyperClick`

## Usage

HyperClick gives you four different ways to navigate, that you can choose based
on your preference.

### 1. Phantoms on hover (Sublime >= 3118)
If you are using the most recent build of sublime, you can just hover over the
required line and an arrow button will appear at the end of line that you can
click and navigate to the destination file. See gif animation file above.

### 2. Phantoms on cursor line (Sublime >= 3118)
Having your cursor on a required/imported line will also show the navigation button
just like hovering over the line.

### 3. Context Menu
If you right click on a required/imported line you'll get a
`Jump To Source File ➜` menu item on the context menu.

<img width="748" alt="sublimehyperclickcontext" src="https://cloud.githubusercontent.com/assets/3202/19578923/480cacde-971e-11e6-9504-91c26737c486.png">

### 4. Shortcut key
By default, HyperClick is using `F12` (sublime's default `Go to definition`) shortcut.
This does not override the default functionality since it's only using it in contexts
that Sublime's self `Go to definition` can not help you navigate.
You can still customize the shortcut by adding this code to your own key-binding
settings.

```json
{
    "keys": ["f12"],
    "command": "hyper_click_jump",
    "context": [{ "key": "hyper_click_jump_line", "operand": true }]
}
```

## Settings
You can customize HyperClick settings by going to
`Preferences > Package Settings > HyperClick > Settings`

#### Disable Annotations (phantom arrow button)
If you don't like the arrow button, you can disable them by setting
`annotations_enabled` to `false`

#### Change Annotations contents
HyperClick uses a greenish button with `➜` when it finds the destination
file and a reddish button with `✘`. These symbols can be customized too.

```json
{
  "annotation_found_text": "➜",
  "annotation_not_found_text": "✘"
}
```

#### Default Settings
see [hyper_click.sublime-settings](https://github.com/aziz/SublimeHyperClick/blob/master/hyper_click.sublime-settings) for up to date settings

```json
{
  "supported_syntaxes": {
    "js": [
      "ecmascript.sublime-syntax",
      "JavaScript.sublime-syntax",
      "JavaScript (Babel).sublime-syntax",
      "JavaScriptNext.tmLanguage"
    ],
    "sass": [
      "SCSS.tmLanguage",
      "Sass.tmLanguage"
    ],
    "less": [
      "LESS.tmLanguage"
    ],
    "php": [
      "PHP.sublime-syntax",
      "PHP Source.sublime-syntax"
    ],
    "stylus": [
      "Stylus.tmLanguage"
    ],
    "html": [
      "HTML.sublime-syntax"
    ],
    "jstl": [
      "jstl.tmLanguage"
    ]
  },
  "import_line_regex": {
    "js": [
      "^import\\s+['\"](.+)['\"];?$",
      ".*from\\s+['\"](.+)['\"];?$",
      ".*require\\(['\"](.+?)['\"]\\).*"
    ],
    "sass": [
      "^@import\\s+['\"](.+)['\"];?$"
    ],
    "less": [
      "^@import\\s+\\(?.*\\)?\\s*['\"](.+)['\"];?$"
    ],
    "php": [
      "^import\\(['\"](.+)['\"]\\);?$",
      "^import_once\\(['\"](.+)['\"]\\);?$",
      "^require\\(['\"](.+)['\"]\\);?$",
      "^require_once\\(['\"](.+)['\"]\\);?$"
    ],
    "stylus": [
      "^@import\\s+['\"](.+)['\"];?$"
    ],
    "html": [
      ".*?<link\\s+rel=\"import\"\\s+href=['\"](.+)['\"]/?>.*?"
    ],
    "jstl": [
      "(<([\\w-]*)\\:([\\w-]*))",
    ]
  },
  "valid_extensions": {
    "js": ["js", "jsx"],
    "sass": ["scss", "sass"],
    "less": ["less"],
    "php": ["php"],
    "stylus": ["styl", "stylus"],
    "html": ["html"],
    "jstl": ["jsp", "tag"]
  },
  "default_filenames": {
    "js": ["index"]
  },
  "vendor_dirs": {
    "js": ["node_modules"],
    "html": ["node_modules", "bower_components"],
    "jstl": ["WEB-INF"]
  },
  "lookup_paths": {
    "js": [],
    "jstl": [
      "taglib *prefix ?= ?[\"'](.*)[\"'] *tagdir ?= ?[\"'](.*)[\"']",
      "xmlns:(\\w*)=[\"']urn:jsptagdir:(.*?)[\"']"
    ]
  },
  "annotation_found_text": "➜",
  "annotation_not_found_text": "✘",
  "annotations_enabled": true
}
```

## License
Copyright 2016-2017 [Allen Bargi](https://twitter.com/aziz). Licensed under the MIT License
