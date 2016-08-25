from wsgiref.simple_server import make_server
from cgi import parse_qs
from factory import *


def form(env):
    cl = int(env.get("CONTENT_LENGTH", "0"))
    d = env.get("wsgi.input")
    d_d = parse_qs(d.read(cl).decode("utf-8"))
    armies_num = int(d_d.get("armies_num")[0])
    factory = Factory()
    battlefield = factory.create_battlefield(armies_num)
    return battlefield.start()


route = {"form": form}


def app(env, resp_start):
    resp_start('200 OK', [('content-type', 'text/html')])
    qs = env.get('QUERY_STRING')
    path = env.get('PATH_INFO', '/')[1:]
    parts = path.split('/')

    if len(parts) > 0 and parts[0]:
        fn = route.get(parts[0])
        if fn is not None:
            text = fn(env)
    else:
        text = ""

    with open("index.html", "r") as f:
        res = f.read().format(text).encode("utf-8")
    return [res]


if __name__ == '__main__':
    serv = make_server('', 8080, app)
    serv.serve_forever()
    serv.shutdown()
