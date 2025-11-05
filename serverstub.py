from typing import Any, Dict
from datastore import Datastore


class ServerStub:

    def __init__(self, impl: Datastore):
        self.impl = impl
        self.methods = {
            "write": impl.write,
            "read": impl.read,
        }

    def dispatch(self, request: Dict[str, Any]) -> Dict[str, Any]:

        request_id = request.get("request_id")
        method_name = request.get("method")
        args = request.get("args", [])
        kwargs = request.get("kwargs", {})

        try:
            if method_name not in self.methods:
                raise ValueError(f"Unknown method: {method_name}")

            # excecute the method
            method = self.methods[method_name]
            result = method(*args, **kwargs)

            return {
                "type": "response",
                "status": "success",
                "result": result,
                "request_id": request_id
            }

        except Exception as e:
            return {
                "type": "response",
                "status": "error",
                "error": type(e).__name__,
                "message": str(e),
                "request_id": request_id
            }