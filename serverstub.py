from typing import Any, Dict
from datastore import Datastore


class ServerStub:
    """Server-side stub for method dispatch"""

    def __init__(self, impl: Datastore):
        self.impl = impl
        self.methods = {
            "write": impl.write,
            "read": impl.read,
        }

    def dispatch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a request to the appropriate method

        Args:
            request: The request message

        Returns:
            Response message
        """
        request_id = request.get("request_id")
        method_name = request.get("method")
        args = request.get("args", [])
        kwargs = request.get("kwargs", {})

        try:
            if method_name not in self.methods:
                raise ValueError(f"Unknown method: {method_name}")

            # Invoke the method
            method = self.methods[method_name]
            result = method(*args, **kwargs)

            # Create success response
            return {
                "type": "response",
                "status": "success",
                "result": result,
                "request_id": request_id
            }

        except Exception as e:
            # Create error response
            return {
                "type": "response",
                "status": "error",
                "error": type(e).__name__,
                "message": str(e),
                "request_id": request_id
            }