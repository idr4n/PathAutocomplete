import os
import re
import sublime
import sublime_plugin

SETTINGS_FILE = 'PathAutocomplete.sublime-settings'
s = {}


def plugin_loaded():
    global s
    s = sublime.load_settings(SETTINGS_FILE)


def debug(var, message=''):
    print('Path Debug - %s: %s' % (message, var))


def resolve_path(view, path: str):
    if view.file_name():
        dirname = os.path.dirname(view.file_name())
    else:
        dirname = os.path.expanduser('~')

    if path.startswith(".%s" % os.sep):
        return path.replace(".%s" % os.sep, dirname + os.sep)

    if path.startswith("..%s" % os.sep):
        num_parents = len(path.split('../')) - 1
        parent_path = os.path.dirname(dirname)
        for _ in range(1, num_parents):
            parent_path = os.path.dirname(parent_path)

        regex = r"^(\.\.%s){1,}" % os.sep
        match = re.match(regex, path).group(0)
        return path.replace(match, parent_path + os.sep)


def completion_item(dirname: str, basename: str):
    details = '''
    <i>In: <a href="">%s</a></i>
    ''' % (dirname)

    return sublime.CompletionItem(
        basename,
        annotation=path_type(dirname, basename),
        kind=(sublime.KIND_ID_SNIPPET, 'p', 'Path'),
        details=details
    )


def path_type(dirname, basename):
    if os.path.isdir(os.path.join(dirname, basename)):
        return 'Dir'
    elif os.path.isfile(os.path.join(dirname, basename)):
        return 'File'
    else:
        return 'path'


class PathCompletions(sublime_plugin.ViewEventListener):
    paths = []
    dirname = ''

    def on_modified_async(self):
        triggers = s.get('triggers')
        region = self.view.extract_scope(self.view.sel()[0].a-1)
        region_str = self.view.substr(region)
        quote_type = '"'

        if region_str and region_str[0] in triggers:
            quote_type = region_str[0]

            split = '%s' % quote_type
            path = self.view.substr(region).split(split)[1].strip("'\"")
            path = os.path.expanduser(path)

            if (path.startswith(".%s" % os.sep)
                    or path.startswith("..%s" % os.sep)):
                path = resolve_path(self.view, path)

            if ((os.path.isdir(path) and path.endswith(os.sep))
                    or os.path.dirname(path)):
                if os.path.dirname(path):
                    path = os.path.dirname(path)
                try:
                    dirs = os.listdir(path)
                    self.paths = sorted(dirs)
                    self.dirname = path
                except Exception:
                    self.paths = []

        else:
            self.paths = []

    def on_query_completions(self, prefix, locations):
        if sublime.version() < '4050':
            return ["%s\t%s" % (path, path_type(self.dirname, path))
                    for path in self.paths]
        else:
            pathslist = [completion_item(self.dirname, path)
                         for path in self.paths]

            return sublime.CompletionList(pathslist)
