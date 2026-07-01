from . import superjob
from . import rabota

PARSERS = {
    'superjob': superjob,
    'rabota': rabota,
}

def get_parser(name):
    return PARSERS.get(name, None)