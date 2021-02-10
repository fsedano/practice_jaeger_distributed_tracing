import logging
import time
from jaeger_client import Config

if __name__ == "__main__":
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


    for i in range(1,100000):
        with tracer.start_span(f'TestSpan{i}') as span:
            span.log_kv({'event': f'test message parent {i}', 'life': 42})

            with tracer.start_span('ChildSpan', child_of=span) as child_span:
                time.sleep(3)
                child_span.log_kv({'event': f'down below iteration {i}'})
                time.sleep(5)
                child_span.log_kv({'event': f'down below iteration {i} - second'})

    time.sleep(2)   # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
    tracer.close()  # flush any buffered spans