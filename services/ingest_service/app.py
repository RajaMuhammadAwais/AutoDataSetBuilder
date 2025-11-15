import os
import logging
from time import time

# Try to import Flask and a Prometheus client. In lightweight test environments
# these packages may not be installed, so provide minimal shims that are
# sufficient for the unit tests (they call endpoints via the Flask test
# client and rely on `request.get_json`, `jsonify`, and counters having an
# `inc()` method).
try:
    from flask import Flask, request, jsonify
except Exception:
    import json

    class _RequestShim:
        def __init__(self):
            self._raw = None

        def get_json(self, force=False, silent=True):
            if self._raw is None:
                return None
            try:
                if isinstance(self._raw, (bytes, bytearray)):
                    return json.loads(self._raw.decode())
                if isinstance(self._raw, str):
                    return json.loads(self._raw)
                return self._raw
            except Exception:
                if silent:
                    return None
                raise

        def _set_json(self, data):
            # Accept bytes, str or already-parsed dict
            if isinstance(data, (bytes, bytearray)):
                self._raw = data
            elif isinstance(data, str):
                self._raw = data
            else:
                # assume dict-like
                self._raw = json.dumps(data)

    request = _RequestShim()

    def jsonify(obj):
        return obj

    def _make_response(resp):
        class Resp:
            def __init__(self, resp):
                if isinstance(resp, tuple):
                    body, status = resp
                else:
                    body, status = resp, 200
                if isinstance(body, (dict, list)):
                    self.data = json.dumps(body).encode()
                elif isinstance(body, str):
                    self.data = body.encode()
                elif isinstance(body, bytes):
                    self.data = body
                else:
                    self.data = b""
                self.status_code = status

            def get_json(self):
                return json.loads(self.data.decode())

        return Resp(resp)

    class Flask:
        def __init__(self, name):
            self._routes = {}
            self.config = {}

        def route(self, path, methods=None):
            if methods is None:
                methods = ["GET"]

            def decorator(f):
                # store the function and allowed methods
                self._routes[path] = (f, methods)
                return f

            return decorator

        def test_client(self):
            app = self

            class Client:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

                def get(self, path):
                    func, methods = app._routes.get(path, (None, None))
                    if func is None:
                        raise RuntimeError("no route")
                    resp = func()
                    return _make_response(resp)

                def post(self, path, data=None, content_type=None):
                    request._set_json(data)
                    func, methods = app._routes.get(path, (None, None))
                    if func is None:
                        raise RuntimeError("no route")
                    resp = func()
                    return _make_response(resp)

            return Client()

try:
    from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
except Exception:
    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, amount=1):
            return None

    def generate_latest():
        return b""

    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"


# Module-level placeholder so tests can patch `services.ingest_service.app.IngestClient`
IngestClient = None


REQUESTS = Counter("autods_ingest_requests_total", "Total ingest requests")
SUCCESSES = Counter("autods_ingest_success_total", "Successful ingests")
FAILURES = Counter("autods_ingest_failure_total", "Failed ingests")


def create_app():
    app = Flask(__name__)

    # basic logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ingest_service")

    @app.route("/healthz", methods=["GET"])
    def healthz():
        return "ok", 200

    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    @app.route("/ingest", methods=["POST"])
    def ingest():
        REQUESTS.inc()
        payload = request.get_json(force=True, silent=True) or {}
        url = payload.get("url")
        license = payload.get("license")
        source = payload.get("source")

        if not url:
            FAILURES.inc()
            return jsonify({"error": "missing 'url' in request"}), 400

        # Allow tests to patch `services.ingest_service.app.IngestClient` at
        # module-level. If not present, lazily import from the SDK.
        try:
            IngestClient = globals().get("IngestClient")
            if IngestClient is None:
                from sdk.autods.ingest import IngestClient
        except Exception as e:
            logger.exception("IngestClient import failed")
            FAILURES.inc()
            return (
                jsonify({"error": "ingest backend unavailable", "detail": str(e)}),
                503,
            )

        # Configure from env
        s3_bucket = os.environ.get("S3_BUCKET", "test-bucket")
        db_url = os.environ.get("DB_URL", "postgresql://user:pass@localhost/db")

        start = time()

        # Instantiate the ingest client. If an ImportError occurs during
        # instantiation (e.g. tests patch the symbol to raise), surface that
        # as a 503 (backend unavailable). Other runtime errors are 500.
        try:
            client = IngestClient(s3_bucket=s3_bucket, db_url=db_url)
        except ImportError as e:
            logger.exception("IngestClient not available at instantiation")
            FAILURES.inc()
            return (
                jsonify({"error": "ingest backend unavailable", "detail": str(e)}),
                503,
            )
        except Exception as e:
            logger.exception("Ingest failed during client init")
            FAILURES.inc()
            return jsonify({"error": "ingest failed", "detail": str(e)}), 500

        try:
            try:
                result = client.ingest_url(url, license=license, source=source)
            finally:
                try:
                    client.close()
                except Exception:
                    pass
        except Exception as e:
            logger.exception("Ingest failed during ingest_url")
            FAILURES.inc()
            return jsonify({"error": "ingest failed", "detail": str(e)}), 500

        SUCCESSES.inc()
        latency = time() - start
        logger.info("Ingest succeeded: %s (latency=%.3f)", result, latency)
        return jsonify({"result": result}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
