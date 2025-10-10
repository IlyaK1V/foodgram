import os


def print_tree(path='.', indent=''):
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        print(indent + name)
        if os.path.isdir(full_path) and name not in ('venv', '__pycache__'):
            print_tree(full_path, indent + '    ')


print_tree('.')
