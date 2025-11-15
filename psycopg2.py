# Lightweight psycopg2 stub for test environments without the real package
class OperationalError(Exception):
    pass

def connect(*args, **kwargs):
    raise OperationalError("psycopg2 not installed")
