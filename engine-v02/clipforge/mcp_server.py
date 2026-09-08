"""Optional stdio MCP adapter for Hermes and other MCP-capable harnesses."""
from .control import execute


def make_server(config_path):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise RuntimeError("Install MCP support with: python -m pip install -e '.[agent]'") from None
    server = FastMCP("ClipForge")

    @server.tool()
    def submit_video(source: str, profile: str | None = None) -> dict:
        """Queue an authorized local video path or a single HTTP(S) video URL. Returns an ID immediately."""
        return execute(config_path, "submit", source=source, profile=profile)

    @server.tool()
    def processing_status() -> dict:
        """Get worker, download and editing status, including finished clip paths and errors."""
        return execute(config_path, "status")

    @server.tool()
    def model_profiles() -> dict:
        """List preconfigured text/transcription model profiles. Does not disclose API-key values."""
        return execute(config_path, "profiles")

    @server.tool()
    def available_models(profile: str | None = None) -> dict:
        """List model IDs offered by a configured OpenAI-compatible endpoint."""
        return execute(config_path, "models", profile=profile)

    @server.tool()
    def select_profile(profile: str) -> dict:
        """Choose an existing model profile for future submissions; empty string selects base settings."""
        return execute(config_path, "use-profile", profile=profile)

    @server.tool()
    def select_model(model_id: str, profile: str | None = None) -> dict:
        """Set an endpoint model ID for a profile's next processing jobs. List available_models first."""
        return execute(config_path, "set-model", identifier=model_id, profile=profile)

    @server.tool()
    def worker_control(action: str) -> dict:
        """Start, pause, resume or stop the built-in worker. Use action start/pause/resume/stop."""
        if action not in ("start", "pause", "resume", "stop"):
            raise ValueError("Unsupported worker action")
        return execute(config_path, action)

    @server.tool()
    def retry_failed(identifier: str, download: bool = False) -> dict:
        """Retry a failed/deferred editing job or download by its exact ID."""
        return execute(config_path, "retry-download" if download else "retry", identifier=identifier)

    return server


def serve_mcp(config_path):
    make_server(config_path).run(transport="stdio")
