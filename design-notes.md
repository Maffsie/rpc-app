# RPC

a puppy is taking your requests and doing some very good boy things
and letting you know what the result was. please pet the puppy.

## Design ideas

The design of this application might be a bit odd. My idea was to
have each version of the API segregated and responsible for itself,
and within each version of the API, each 'category' or 'segment' would
in turn be responsible for itself.

In an ideal world, this would be dynamically loaded at runtime, such
that if you had the following file structure:

```
RPC
- v1
-- __init__.py
-- health.py
- v2
-- __init__.py
-- health.py
- unversioned
-- __init__.py
-- ping.py
- __init__.py
```

The initial `__init__.py` (the `RPC` module) would not contain any
references to `v1`, `v2`, `unversioned` or any of the modules within,
and the `__init__.py` in each iteration of the API
(ex. `v1`, `unversioned`), would not have any references to their
own modules or classes.

Ideally, `RPC` on its own would simply initialise the API server,
including configuration and any startup tasks. The initialisation
would dynamically discover the available 'versions' and default their
URI prefix to the given `__name__` of the modules, unless a prefix is
explicitly specified (useful for `unversioned`).

As each API version is discovered, it would be registered to the
API server, and it would in turn discover its available modules,
and register them in turn. Those modules would contain functions
which have routes declared as decorators. eg., in `v1/health.py`,
one would see the following:

```python
from RPC import route
from RPC.methods import GET, HEAD

@route([GET, HEAD,])
def alive():
    return True
```

The resulting route being `/v1/health/alive`, which would respond to
the HTTP methods 'GET' and 'HEAD'. The chain of events leading from
the receipt of the HTTP request, and the transmission of the
response, would have the `return True` transformed into something
like (for a GET request) `{status: "success"}` or a simple HTTP 200
response (for a HEAD request).

Of importance is that the routes would be entirely inferred by the
structure. `/v1` would be registered by the version of the API,
`/health` would be inferred by the module, and `/alive` would be
inferred by the name of the method the route is assigned to.

A function could explicitly declare its route with the following:

```python
from RPC import route
from RPC.methods import GET, HEAD

@route("/heartbeat", [GET, HEAD,])
def alive():
    return True
```

It is relatively easy to infer arguments by type, making the
end experience very nice, though explicitly specifying argument
names would of course also work
(`@route(path="/heartbeat", methods=...)`).

An API version would be defined in its `__init__.py`, similar to:

```python
from RPC import VersionedApi

this = VersionedApi()
```

Imagining that VersionedApi would do some magical setup stuff
in its `__init__` function. The version could be inferred from
the module `__name__`, but could also be specified manually:

```python
this = VersionedApi("/")
```

## The as-built

As built, this is a very different piece of software to what I
ideally imagine it would be.
The API versions are, by necessity, fully aware of their
subordinate modules, and the core RPC module is fully aware of each
API version.

An API module and route is declared, for example in `ping.py`,
like so:

```python
from flask import Blueprint

routes = Blueprint(__name__, __name__, url_prefix="/")

@routes.route("/ping")
def ping():
    return "pong"
```

An API version is declared in its `__init__.py` as:

```python
from flask import Blueprint

from .module1 import routes as routes1
from .module2 import routes as routes2
from .module3 import routes as routes3

api = Blueprint(__name__, __name__, url_prefix="/vX")
[api.register_blueprint(module) for module in (routes1, routes2, routes3)]
```

And similarly, in the root `__init__.py`, the API versions are
registered as such:

```python
from flask import Flask

def create_app():
    from .Unversioned import api as api_unver
    from .v1 import api as api_v1

    app = Flask(__name__)
    [app.register_blueprint(version) for version in (api_unver, api_v1)]
    return app
```

While this is functional and does work, I really don't enjoy it.

Raw Flask is powerful, but I really desire flexibility and a
level of "automagic" that I can trust to work. Another example is
that, as built, output is entirely up to the route handler.

Given the hypothetical API endpoint `/v1/generate/uuid` which would
respond with a new randomly-generated UUIDv4, in RPC as built, this
would respond with whatever the UUID-generating function is built to
return. Example:

```python
@routes.route("/uuid")
def gen_uuid():
    return str(random_uuid())
```

In all scenarios, this would yield a response with only the text
of the given UUID.

Ideally, the application would translate this into whichever
content type was requested by the invoker. What if the request
included `Accept: application/json`, or the request URI was
`/v1/generate/uuid.json`? The endpoint should not need to have
implementation details specific to that scenario. Ideally, the
handler would simply return a UUID, and RPC itself would serialise
that UUID object into the requested format. `text/plain` would
return the raw UUID, `application/json` would return
`{uuid: "<uuid>", result: "success"}`, `application/yaml` would
return a middle-finger emoji.

## Alternative design considerations

I considered several Flask extension modules in planning this
project:

* [Flask-RESTful][1], last activity was nearly a year ago, last release in 2014
* [Flask-RESTx][2], a fork of the abandoned Flask-RESTPlus
* [Flask-RESTless-NG][3], a fork of the abandoned Flask-RESTless

There were also several alternatives that I wrote off immediately:

* [Connexion][4], which expects you to build from a Swagger document
* [Zappa][5], which almost seems to only be a deployment tool
* [Flask-Potion][6], which simply looked heavy and not what I want
* [Eve][7], which looked promising, but expects you to use MongoDB

[1]: http://flask-restful.readthedocs.io/
[2]: https://flask-restx.readthedocs.io/en/latest/
[3]: https://flask-restless-ng.readthedocs.io/en/latest/
[4]: https://connexion.readthedocs.io/en/latest/
[5]: https://github.com/zappa/Zappa
[6]: https://potion.readthedocs.io/en/latest/
[7]: https://docs.python-eve.org/en/stable/index.html
