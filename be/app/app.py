import logging
import time
from jaeger_client import Config
from flask import Flask
from flask import request
import requests
from opentracing.ext import tags
from opentracing.propagation import Format


log_level = logging.DEBUG
logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

config = Config(
    config={ # usually read from some yaml config
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },
    service_name='app-be',
    validate=True,
)
# this call also sets opentracing.tracer
tracer = config.initialize_tracer()
#from flask_opentracing import FlaskTracing
app = Flask(__name__)
#tracing = FlaskTracing(tracer, True, app)


@app.route('/ep1')
def ep1_handler():
    logging.error(f"Request of EP1. Hdr={request.headers}")
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
    with tracer.start_active_span('be', child_of=span_ctx, tags=span_tags):
        time.sleep(2)
        return "EP1 requested"


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
