import uuid

from RPC.util.base import Api

routes = Api()


@routes.route("/uuid")
async def unversioned_uuid():
    return {
        "status": 200,
        "uuid": uuid.uuid4(),
    }


@routes.route("/uuid/<int:version>")
@routes.route("/uuid/v<int:version>")
async def versioned_uuid(version: int):
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


@routes.route("/uuid/<int:version>/<string:uuidtype>/<string:uuidns>")
@routes.route("/uuid/v<int:version>/<string:uuidtype>/<string:uuidns>")
async def namespaced_uuid(version: int, uuidtype: str, uuidns: str):
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
