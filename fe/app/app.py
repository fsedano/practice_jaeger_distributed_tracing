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
    service_name='app-fe',
    validate=True,
)
# this call also sets opentracing.tracer
tracer = config.initialize_tracer()
from flask_opentracing import FlaskTracing
app = Flask(__name__)
tracing = FlaskTracing(tracer, True, app)

def f1(data):
    with tracer.start_active_span('format') as scope:
        scope.span.log_kv({'event': 'string-format', 'value':data})


def http_get(port, path, param, value):
    url = f"http://be:{port}/{path}"
    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)
    r = requests.get(url, params={param: value}, headers=headers)
    return r.text

@app.route('/hello')
@tracing.trace()
def hello_handler():
    current_span = tracing.get_span(request)
    with tracer.start_active_span('my-test-span2') as scope:
        scope.span.set_tag('tag1k', "tag1v")
        family = 'one big family'
        scope.span.log_kv({'event': 'string-format', 'value':f'we are {family}'})
        scope.span.log_kv({'event': 'println'})
        f1('pepe')

    logging.error(f"Span is {current_span}")
    with tracer.start_span('call-api', child_of=current_span) as span:
        span.set_tag("http.url", "http://www.cisco.com")
        r = requests.get("http://www.cisco.com")
        span.set_tag("http.status_code", r.status_code)
    return "Hola"

@app.route('/hello2')
@tracing.trace()
def hello2_handler():
    with tracer.start_active_span('call-be') as scope:
        p_val = request.args.get('a')
        logging.error(f"Param is {p_val}")
        scope.span.set_baggage_item('parameters', p_val)
        data = http_get(5000, 'ep1','','')
        scope.span.log_kv({'event': 'string-format', 'value':data})
        return data


@app.route('/bye')
@tracing.trace()
def bye_handler():
    return "Bye"

@app.route('/healthz')
@tracing.trace()
def healtz_handler():
    return "OK"


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

time.sleep(2)   # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
tracer.close()  # flush any buffered spans