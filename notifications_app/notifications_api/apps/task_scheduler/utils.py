def object_to_fully_qualified_name(func) -> str:
    try:
        ref = f"{func.__module__}:{get_callable_name(func)}"
        func2 = fully_qualified_name_to_obj(ref)
        if func != func2:
            raise ValueError
    except Exception:
        raise ValueError(f"Cannot determine the reference to {func}")
    return ref


def fully_qualified_name_to_obj(ref):
    """
    Returns the object pointed to by `ref`
    """
    if not isinstance(ref, str):
        raise TypeError("Reference must be string")
    if ":" not in ref:
        raise ValueError("Invalid Reference")
    modulename, rest = ref.split(":", 1)
    try:
        obj = __import__(modulename, fromlist=[rest])
    except ImportError:
        raise LookupError(f"Cannot resolve reference {ref}: could not import module")

    try:
        for name in rest.split("."):
            obj = getattr(obj, name)
            return obj
    except Exception:
        raise LookupError(
            f"Cannot resolve reference {ref}: error looking up the object"
        )


def get_callable_name(func):
    if hasattr(func, "__qualname__"):
        return func.__qualname__
