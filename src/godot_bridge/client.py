"""WebSocket JSON-RPC client for Godot Bridge."""

import json
import os
from pathlib import Path
from typing import Any
from loguru import logger
from pydantic import BaseModel


class GodotConfig(BaseModel):
    """Connection configuration."""
    ws_url: str = "ws://127.0.0.1:49631"
    token: str = ""
    token_file: str = ""


class RPCError(Exception):
    """JSON-RPC error from Godot."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"RPC Error {code}: {message}")


class GodotClient:
    """Synchronous WebSocket client for Godot Editor."""

    def __init__(self, config: GodotConfig | None = None):
        self.config = config or self._load_config()
        self.ws = None
        self.request_id = 0
        self.authenticated = False

    def _load_config(self) -> GodotConfig:
        """Load config from environment."""
        ws_url = os.environ.get("GODOT_WS_URL", "ws://127.0.0.1:49631")
        token = os.environ.get("GODOT_TOKEN", "")
        token_file = os.environ.get("GODOT_TOKEN_FILE", "")

        # Try to read token from file
        if not token and token_file:
            token_path = Path(token_file)
            if token_path.exists():
                content = token_path.read_text().strip()
                # Handle JSON format (GodotBridge uses JSON with token field)
                try:
                    data = json.loads(content)
                    token = data.get("token", content)
                    # Also get port from JSON if available
                    if "port" in data:
                        ws_url = f"ws://127.0.0.1:{data['port']}"
                    logger.debug(f"Loaded token from JSON file {token_file}")
                except json.JSONDecodeError:
                    # Plain text token
                    token = content
                    logger.debug(f"Loaded token from {token_file}")

        return GodotConfig(ws_url=ws_url, token=token, token_file=token_file)

    def connect(self) -> bool:
        """Connect and authenticate with Godot."""
        try:
            import websockets.sync.client as ws_client
            logger.info(f"Connecting to Godot at {self.config.ws_url}...")
            self.ws = ws_client.connect(self.config.ws_url, close_timeout=5)

            # Authenticate
            result = self.call("auth.hello", {
                "token": self.config.token,
                "client": "godot-bridge-cli",
                "version": "1.0.0"
            })

            if result.get("ok"):
                self.authenticated = True
                logger.info(f"Connected to Godot {result.get('editor_version', 'unknown')}")
                return True
            else:
                logger.error("Authentication failed")
                return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call JSON-RPC method on Godot."""
        if self.ws is None:
            raise RuntimeError("Not connected to Godot")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": str(self.request_id),
            "method": method,
            "params": params or {}
        }

        logger.debug(f"RPC call: {method}")
        self.ws.send(json.dumps(request))

        while True:
            response_text = self.ws.recv()
            response = json.loads(response_text)

            if response.get("id") == str(self.request_id):
                if "error" in response:
                    error = response["error"]
                    raise RPCError(
                        error.get("code", -1),
                        error.get("message", "Unknown error"),
                        error.get("data")
                    )
                return response.get("result", {})

    def close(self) -> None:
        """Close connection."""
        if self.ws:
            self.ws.close()
            self.ws = None
            self.authenticated = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()


# Convenience function for single calls
def godot_call(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute single RPC call to Godot."""
    with GodotClient() as client:
        return client.call(method, params)
