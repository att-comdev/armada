def insert_label(data, label):
    label_path = ['spec:', 'template:', 'metadata:', 'labels:']
    return _insert_yaml_entry(data, label, label_path)

def _insert_yaml_entry(data, entry, path):
    '''
    :params data - contents of a yaml as a string
    :params entry - entry to insert into the template yaml

    Returns the original data with the newly inserted entry
    '''
    new_data = ''
    stack = []
    entry_inserted = False
    data_lines = data.splitlines()
    for index, line in enumerate(data_lines):
        new_data += '{}\n'.format(line)
        if entry_inserted or not _is_data(line):
            continue

        stripped_line = line.lstrip(' ')
        line_indent = len(line) - len(stripped_line)
        stack.append((stripped_line.rstrip(), line_indent))

        next_line = ''
        for counter in range(index + 1, len(data_lines) - 1):
            if not _is_data(next_line):
                next_line = data_lines[counter]
        next_line_indent = len(next_line) - len(next_line.lstrip(' '))

        print(stack)
        # need to pop the stack
        # if leaving path, fill in entry; else, pop the stack
        while next_line_indent <= line_indent and stack:
            if _leaving_path([s[0] for s in stack], path):
                new_data += _get_formatted_subpath_and_entry([s[0] for s in stack], entry, path, line_indent)
                entry_inserted = True
                break
            stack.pop()
            line_indent = stack[-1][1] if stack else -1

    if not entry_inserted:
        new_data += _get_formatted_subpath_and_entry([], entry, path, -2)
    return new_data

def _is_data(line):
    if not line or line.lstrip(' ').startswith('#') or line.lstrip(' ').startswith('{{'):
        return False
    return True

def _leaving_path(stack, path):
    '''Returns true if popping the stack would leave the path'''
    deepest_path_index = _get_deepest_path_index(stack, path)
    if deepest_path_index == -1:
        return False
    return deepest_path_index == len(stack) - 1

def _get_deepest_path_index(stack, path):
    deepest_path_index = -1
    for entry in path:
        try:
            entry_index = stack.index(entry)
            if entry_index <= deepest_path_index:
                break
            deepest_path_index = entry_index
        except ValueError:
            break
    return deepest_path_index

def _get_formatted_subpath_and_entry(stack, entry, path, current_indent):
    filled_path_and_entry = ''
    indent = current_indent + 2
    remaining_subpath = _get_remaining_subpaths(stack, path)
    for subpath in remaining_subpath:
        filled_path_and_entry += '{}{}\n'.format(' ' * indent, subpath)
        indent += 2
    filled_path_and_entry += '{}{}\n'.format(' ' * indent, entry)
    return filled_path_and_entry
    
def _get_remaining_subpaths(stack, path):
    deepest_path_index = -1
    path_index = 0
    for entry in path:
        try:
            entry_index = stack.index(entry)
            if entry_index <= deepest_path_index:
                break
            deepest_path_index = entry_index
        except ValueError:
            break
        path_index += 1
    return path[path_index:]
