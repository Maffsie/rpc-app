import uuid

from flask import Blueprint, current_app

generators = Blueprint("gen", __name__, url_prefix="/gen")


@generators.route("/uuid")
def unversioned_uuid():
    return {
        "status": 200,
        "uuid": uuid.uuid4(),
    }


@generators.route("/uuid/<int:version>")
@generators.route("/uuid/v<int:version>")
def versioned_uuid(version: int):
    resp = {
        "uuid": "",
    }
    match version:
        case 1:
            resp["uuid"] = uuid.uuid1()
        case 4:
            resp["uuid"] = uuid.uuid4()
        case 3 | 5:
            return {
                "status": 401,
                "error": "insufficient data to generate UUID",
            }
        case _:
            return {
                "status": 401,
                "error": "unknown UUID version",
            }
    return {"status": 200, **resp}


@generators.route("/uuid/<int:version>/<string:uuidtype>/<string:uuidns>")
@generators.route("/uuid/v<int:version>/<string:uuidtype>/<string:uuidns>")
def namespaced_uuid(version: int, uuidtype: str, uuidns: str):
    resp = {
        "uuid": "",
    }
    nstype = uuid.RESERVED_NCS
    match uuidtype.lower():
        case "dns":
            nstype = uuid.NAMESPACE_DNS
        case "url" | "uri":
            nstype = uuid.NAMESPACE_URL
        case "oid":
            nstype = uuid.NAMESPACE_OID
        case "x500" | "x.500":
            nstype = uuid.NAMESPACE_X500
        case _:
            return {
                "status": 401,
                "error": "unrecognised namespace for UUID",
            }
    match version:
        case 3:
            resp["uuid"] = uuid.uuid3(namespace=nstype, name=uuidns)
        case 5:
            resp["uuid"] = uuid.uuid5(namespace=nstype, name=uuidns)
        case _:
            return {
                "status": 401,
                "error": "unrecognised UUID version",
            }
    return {"status": 200, **resp}
