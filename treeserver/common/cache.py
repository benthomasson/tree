fn_cache = {}

def fn_memoize(fn):
    def _new(name):
        if name not in fn_cache:
            fn_cache[name]=fn(name)
        return fn_cache[name]
    return _new

