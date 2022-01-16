from src.constants import OK_MOVED_STATUS_CODES


def resolve_status(f: callable, *args, **kwargs):
    content, status = f(*args, **kwargs)

    if status.value in OK_MOVED_STATUS_CODES:
        return content, status.value, None
    return None, status.value, content["message"]
