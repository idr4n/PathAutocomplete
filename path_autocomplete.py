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
        for i in range(1, num_parents):
            parent_path = os.path.dirname(parent_path)

        regex = r"^(\.\.%s){1,}" % os.sep
        match = re.match(regex, path).group(0)
        return path.replace(match, parent_path + os.sep)


def path_type(dirname, basename):
    if os.path.isdir(os.path.join(dirname, basename)):
        return 'Dir'
    elif os.path.isfile(os.path.join(dirname, basename)):
        return 'File'
    else:
        return 'path'


# def find_region(regions: list, cursor_pos):
#     for region in regions:
#         if region.contains(cursor_pos):
#             return region


class PathCompletions(sublime_plugin.ViewEventListener):
    paths = []
    dirname = ''

    def on_modified_async(self):
        # triggers = ["'", '"']
        triggers = s.get('triggers')
        region = self.view.extract_scope(self.view.sel()[0].a-1)
        region_str = self.view.substr(region)
        quote_type = '"'

        # # line = self.view.line(self.view.sel()[0]).a
        # inquotes = self.view.find_all(r'"(.*?)"')
        # if inquotes:
        #     # debug(inquotes, 'inquotes')
        #     # debug(self.view.sel()[0], 'cursor')
        #     found_region = find_region(inquotes, self.view.sel()[0])
        #     if found_region:
        #         debug(self.view.substr(found_region))

        if region_str and region_str[0] in triggers:
            quote_type = region_str[0]

            split = '%s' % quote_type
            path = self.view.substr(region).split(split)[1].strip("'\"")
            debug(self.view.substr(region).split('"'), 'the path is')
            path = os.path.expanduser(path)

            if (path.startswith(".%s" % os.sep)
                    or path.startswith("..%s" % os.sep)):
                path = resolve_path(self.view, path)
                # print('path is...', path)

            if ((os.path.isdir(path) and path.endswith(os.sep))
                    or os.path.dirname(path)):
                if os.path.dirname(path):
                    path = os.path.dirname(path)
                # print("yes, is dir")
                try:
                    dirs = os.listdir(path)
                    self.paths = sorted(dirs)
                    self.dirname = path
                except Exception:
                    self.paths = []

        else:
            self.paths = []

    def on_query_completions(self, prefix, locations):
        # if not self.view.match_selector(locations[0], "source.python"):
        #     return []
        # print(self.paths)

        # return list(map(add_info, self.paths))
        return ["%s\t%s" % (path, path_type(self.dirname, path))
                for path in self.paths]
