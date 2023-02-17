from importlib import import_module as _import_module
from pkgutil import get_loader as _loader
from pkgutil import iter_modules as _iter_modules


def get_providers():
    _providers = [
        getattr(mod, "p_cls")
        for mod in [
            _import_module(name)
            for _, name, _ in _iter_modules(
                [_loader(__name__).get_filename().rpartition("/")[0]], __name__ + "."
            )
        ]
        if hasattr(mod, "p_cls")
    ]
    return {cls.__module__.rpartition(".")[2]: cls() for cls in _providers}
