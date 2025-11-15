# Local psycopg2 shim inside sdk/ to satisfy tests that insert sdk/ into sys.path
class OperationalError(Exception):
    pass

def connect(*args, **kwargs):
    raise OperationalError("psycopg2 not installed (sdk shim)")
