from common.cache import fn_memoize


@fn_memoize
def load_fn(name):
    parts = name.split('.')
    module_name = parts[0]
    module = None
    for part in parts[1:]:
        try:
            module = __import__(module_name)
            module_name += "."
            module_name += part
        except Exception:
            break
    for part in parts[1:]:
        module = getattr(module, part)
    return module

def class_name(a_class):
    return "{0}.{1}".format(a_class.__module__, a_class.__name__)
