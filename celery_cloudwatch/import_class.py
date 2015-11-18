from importlib import import_module


def import_class(name):
    class_data = name.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)
