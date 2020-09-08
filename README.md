# Sublime HyperClick
Quickly and easily jump between your files.
The missing part of `Go to definition` functionality in Sublime.

![sublime hyperclick](https://cloud.githubusercontent.com/assets/3202/19578519/51558bb4-971c-11e6-8ef2-d256da53d1da.gif)

HyperClick detects references to other files and lets you go to them, by pressing a key or clicking on an icon next to the filename. Even package names and filenames without an extension can be detected.

## Supported Languages

- JavaScript, TypeScript
- Vue, Svelte components
- CSS, Sass, SCSS, LESS, Stylus
- HTML
- PHP
- Twig, Smarty, Pug, Nunjucks, Jinja2
- JSTL
- Dart
- SugarML, SugarSS

If you'd like to request another language, [open an issue](https://github.com/aziz/SublimeHyperClick/issues) with an example project in that language.

## Installation
You can install HyperClick via [Sublime Package Control](https://packagecontrol.io/).

## Usage

HyperClick gives you three different ways to navigate:

### 1. Green arrows to the right of paths
In Sublime Text 3, you can "Go to file" by clicking the arrow to the right of the filename.

This arrow shows up when you **hover your mouse cursor** or **move to the line** (with up/down keys, or Goto Line) that contains the filename.

### 2. Context Menu
If you right click on a required/imported line you'll get a `Goto File` menu item on the context menu.

### 3. Shortcut key
HyperClick extends the use of the <kbd>F12</kbd> (`Go to definition`) shortcut, jumping to files when `Go to definition` doesn't work.


## Settings
You can customize HyperClick settings by going to
`Preferences > Package Settings > HyperClick > Settings`

### Project settings

You can use [project settings](https://www.sublimetext.com/docs/3/projects.html) to configure HyperClick to look for files at specific dirs, through the settings `"lookup_paths"` and `"aliases"`.

To open the project settings file, go to `Project > Settings`. If the `Settings` option is grayed out, choose the option `Save Project As...` (right above it) to save it to disk. The `Settings` option can now be clicked.

#### Example

```json
{
	"folders":
	[
		{
			"path": "development/project"
		}
	],
	"settings": {
		"hyper_click": {
			"scopes": {
				"source.sass": {
					"lookup_paths": [
						"assets/css/src/",
						"assets/css/lib/"
					]
				},
				"text.html.smarty": {
					"lookup_paths": [
						"views/templates/"
					]
				}
			}
		}
	}
}
```

### Upgrading settings for 2.0

In 2.0 the settings structure was inverted, and no longer relies on syntax filename mapping. 
Each language is supported via an entry in the "scopes" object, by the language ["scope"](https://www.sublimetext.com/docs/3/scope_naming.html) name. 

To upgrade your settings, the first step is to rearrange the settings to this new structure. Then:

- Remove now unused settings "supported_syntaxes", "default_filenames".
- Rename "import_line_regex" to "regexes" and "valid_extensions" to "extensions".
- Other settings are unchanged.

Example:

```json
{
	"import_line_regex": {
	    "js": [
	        "^import\\s+['\"](.+)['\"];?$"
	    ]
	}
}
```

Becomes:

```json
{
	"scopes": {
		"source.js": {
			"regexes": [
				"^import\\s+['\"](.+)['\"];?$"
			]
		}
	}
}
```
