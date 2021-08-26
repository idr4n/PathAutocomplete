# PathAutocomplete

### Description

A Sublime Text plugin for path autocompletion. Similar to [AutoFileName](https://packagecontrol.io/packages/AutoFileName) but much simplier in my opinion.

I was finding some issues with AutoFileName plugin, so I decided to give path autocompletions a try. The plugin is still in development, but the result so far is something that works for my needs.

Tihs plugin doesn't call autocompletions automatically, only when a syntax scope is detected after typing something like './', '../', '~/', etc., including single or double quotes (or any other trigger included in the settings), and when Sublime 'decides' to show autocompletions or after hitting the default shortcut for autocompletions, e.g. `ctrl+space`.