class OperationalError(Exception):
    pass

def connect(*args, **kwargs):
    raise OperationalError("psycopg2 not installed (stub)")
