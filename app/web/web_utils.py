def is_safe_url(url: str):
    if not url:
        return True

    if url[0] == "/":
        return True
    else:
        return False
