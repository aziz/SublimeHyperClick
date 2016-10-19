# Sublime HyperClick
single line description

## Why

Supported Languages and Syntaxes

|  Language  |                                                Syntaxes                                               |
|------------|-------------------------------------------------------------------------------------------------------|
| Javascript | `ecmascript.sublime-syntax` <br> `JavaScript.sublime-syntax` <br> `JavaScript (Babel).sublime-syntax` |
| Sass       | `SCSS.tmLanguage` <br> `Sass.tmLanguage`                                                              |


## Installation
You can install via [Sublime Package Control]()

Or clone this repo into your SublimeText Packages directory and rename it to `HyperClick`

## Usage
* phantoms
    * on hover
    * on cursor line
* context menu
* shortcut key

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
