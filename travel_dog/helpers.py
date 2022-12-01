import re


def url_to_filename(url):
    return re.sub(r"[^\w\d-]", "_", url)


def update_user(tracer, LD_USER):
    return
