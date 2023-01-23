from flask import Blueprint, current_app

routes = Blueprint(__name__, __name__, url_prefix=f"/{__name__}")


@routes.route("/fritzin")
def fritzbox_s2h(*args, **kwargs):
    current_app.log.verbose(
        msg="wow!",
        extra=[
            args,
            kwargs,
        ],
    )


"""
TODO
- prometheus metrics exporter
"""
