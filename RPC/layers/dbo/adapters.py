from RPC.layers.dbo.simple import WithSQLiteDB


class RPCTokenAdapter(WithSQLiteDB):
    dbo_conf = {
        "db": "/state/db/tokens.db",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_schema()

    def validate_schema(self):
        with self._db() as dbo:



