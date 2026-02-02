"""Godot Bridge CLI - Unified Godot Editor control."""

import json
import sys
from typing import Annotated, Optional

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from .client import GodotClient, RPCError, godot_call

# Configure loguru for stderr
logger.remove()
logger.add(sys.stderr, level="WARNING", format="{message}")

app = typer.Typer(
    name="godot-bridge",
    help="Unified CLI for Godot Editor control via WebSocket",
    no_args_is_help=True,
)
console = Console()

# Common options
JsonOutput = Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")]
Verbose = Annotated[bool, typer.Option("--verbose", "-v", help="Enable debug logging")]


def output_result(data: dict, as_json: bool = False) -> None:
    """Output result in requested format."""
    if as_json:
        print(json.dumps({"ok": True, "data": data}, indent=2))
    else:
        console.print_json(data=data)


def output_error(error: Exception, as_json: bool = False) -> None:
    """Output error in requested format."""
    if as_json:
        err_data = {"type": "rpc_error" if isinstance(error, RPCError) else "error"}
        if isinstance(error, RPCError):
            err_data["code"] = error.code
            err_data["message"] = error.message
            if error.data:
                err_data["details"] = error.data
        else:
            err_data["message"] = str(error)
        print(json.dumps({"ok": False, "error": err_data}, indent=2))
    else:
        console.print(f"[red]Error:[/red] {error}")
    raise typer.Exit(1)


def setup_logging(verbose: bool) -> None:
    """Configure logging level."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format="{time:HH:mm:ss} | {level} | {message}")


# ============================================================================
# PROJECT COMMANDS
# ============================================================================

project_app = typer.Typer(help="Project information and settings")
app.add_typer(project_app, name="project")


@project_app.command("info")
def project_info(json_out: JsonOutput = False, verbose: Verbose = False):
    """Get project information."""
    setup_logging(verbose)
    try:
        result = godot_call("project.get_info")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@project_app.command("autoloads")
def project_autoloads(json_out: JsonOutput = False, verbose: Verbose = False):
    """List autoload singletons."""
    setup_logging(verbose)
    try:
        result = godot_call("project.get_autoloads")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@project_app.command("input-map")
def project_input_map(json_out: JsonOutput = False, verbose: Verbose = False):
    """Get input action mappings."""
    setup_logging(verbose)
    try:
        result = godot_call("project.get_input_map")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@project_app.command("add-input")
def project_add_input(
    action: str,
    key: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Add input action with key binding."""
    setup_logging(verbose)
    try:
        result = godot_call("project.add_input_action", {"action": action, "key": key})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# EDITOR COMMANDS
# ============================================================================

editor_app = typer.Typer(help="Editor state and operations")
app.add_typer(editor_app, name="editor")


@editor_app.command("state")
def editor_state(json_out: JsonOutput = False, verbose: Verbose = False):
    """Get current editor state."""
    setup_logging(verbose)
    try:
        result = godot_call("editor.get_state")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@editor_app.command("logs")
def editor_logs(json_out: JsonOutput = False, verbose: Verbose = False):
    """Get editor logs."""
    setup_logging(verbose)
    try:
        result = godot_call("editor.get_logs")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@editor_app.command("clear-logs")
def editor_clear_logs(json_out: JsonOutput = False, verbose: Verbose = False):
    """Clear editor logs."""
    setup_logging(verbose)
    try:
        result = godot_call("editor.clear_logs")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@editor_app.command("save-all")
def editor_save_all(json_out: JsonOutput = False, verbose: Verbose = False):
    """Save all open scenes."""
    setup_logging(verbose)
    try:
        result = godot_call("editor.save_all")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# SCENE COMMANDS
# ============================================================================

scene_app = typer.Typer(help="Scene management")
app.add_typer(scene_app, name="scene")


@scene_app.command("open")
def scene_open(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Open a scene file."""
    setup_logging(verbose)
    try:
        result = godot_call("editor.open_scene", {"scene_path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@scene_app.command("save")
def scene_save(
    path: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Save current scene."""
    setup_logging(verbose)
    try:
        params = {"scene_path": path} if path else {}
        result = godot_call("editor.save_scene", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@scene_app.command("create")
def scene_create(
    root_type: str,
    path: str,
    name: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Create a new scene."""
    setup_logging(verbose)
    try:
        params = {"root_type": root_type, "scene_path": path}
        if name:
            params["root_name"] = name
        result = godot_call("scene.create_scene", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@scene_app.command("tree")
def scene_tree(json_out: JsonOutput = False, verbose: Verbose = False):
    """Get scene tree hierarchy."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.get_tree")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@scene_app.command("instance")
def scene_instance(
    parent: str,
    scene_path: str,
    name: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Instance a scene as child of parent node."""
    setup_logging(verbose)
    try:
        params = {"parent_path": parent, "scene_path": scene_path}
        if name:
            params["name"] = name
        result = godot_call("scene.instance_scene", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# NODE COMMANDS
# ============================================================================

node_app = typer.Typer(help="Node manipulation")
app.add_typer(node_app, name="node")


@node_app.command("list")
def node_list(
    parent: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """List child nodes."""
    setup_logging(verbose)
    try:
        params = {"parent_path": parent} if parent else {}
        result = godot_call("scene.list_nodes", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("get")
def node_get(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Get node details."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.get_node", {"node_path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("props")
def node_props(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Get node properties."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.get_node_properties", {"node_path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("set")
def node_set(
    path: str,
    props: str,  # JSON string
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Set node properties (pass properties as JSON string)."""
    setup_logging(verbose)
    try:
        properties = json.loads(props)
        result = godot_call("scene.set_node_properties", {
            "node_path": path,
            "properties": properties
        })
        output_result(result, json_out)
    except json.JSONDecodeError as e:
        output_error(ValueError(f"Invalid JSON: {e}"), json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("add")
def node_add(
    parent: str,
    type: str,
    name: str,
    props: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Add a new node."""
    setup_logging(verbose)
    try:
        params = {"parent_path": parent, "type": type, "name": name}
        if props:
            params["properties"] = json.loads(props)
        result = godot_call("scene.add_node", params)
        output_result(result, json_out)
    except json.JSONDecodeError as e:
        output_error(ValueError(f"Invalid JSON: {e}"), json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("remove")
def node_remove(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Remove a node."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.remove_node", {"node_path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("rename")
def node_rename(
    path: str,
    new_name: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Rename a node."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.rename_node", {"node_path": path, "new_name": new_name})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("duplicate")
def node_duplicate(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Duplicate a node."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.duplicate_node", {"node_path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@node_app.command("reparent")
def node_reparent(
    path: str,
    new_parent: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Reparent a node."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.reparent_node", {
            "node_path": path,
            "new_parent_path": new_parent
        })
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# SCRIPT COMMANDS
# ============================================================================

script_app = typer.Typer(help="Script management")
app.add_typer(script_app, name="script")


@script_app.command("read")
def script_read(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Read script content."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.read_text", {"path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@script_app.command("write")
def script_write(
    path: str,
    content: Optional[str] = None,
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Read content from file"),
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Write script content."""
    setup_logging(verbose)
    try:
        if file:
            from pathlib import Path
            content = Path(file).read_text()
        if not content:
            output_error(ValueError("Provide content or --file"), json_out)
        result = godot_call("filesystem.write_text", {"path": path, "content": content})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@script_app.command("assign")
def script_assign(
    node: str,
    script: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Assign script to node."""
    setup_logging(verbose)
    try:
        result = godot_call("scene.assign_script", {
            "node_path": node,
            "script_path": script
        })
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# PLAY COMMANDS
# ============================================================================

play_app = typer.Typer(help="Run and debug")
app.add_typer(play_app, name="play")


@play_app.command("run")
def play_run(json_out: JsonOutput = False, verbose: Verbose = False):
    """Run main scene."""
    setup_logging(verbose)
    try:
        result = godot_call("play.run_main")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@play_app.command("current")
def play_current(json_out: JsonOutput = False, verbose: Verbose = False):
    """Run current scene."""
    setup_logging(verbose)
    try:
        result = godot_call("play.run_current")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@play_app.command("stop")
def play_stop(json_out: JsonOutput = False, verbose: Verbose = False):
    """Stop running game."""
    setup_logging(verbose)
    try:
        result = godot_call("play.stop")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@play_app.command("state")
def play_state(json_out: JsonOutput = False, verbose: Verbose = False):
    """Get play state."""
    setup_logging(verbose)
    try:
        result = godot_call("play.get_state")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# RESOURCE COMMANDS
# ============================================================================

resource_app = typer.Typer(help="Resources (materials, textures, etc.)")
app.add_typer(resource_app, name="resource")


@resource_app.command("material")
def resource_material(
    node: str,
    material_type: str = "StandardMaterial3D",
    props: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Create and apply material to node."""
    setup_logging(verbose)
    try:
        params = {"node_path": node, "material_type": material_type}
        if props:
            params["properties"] = json.loads(props)
        result = godot_call("resources.create_material", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@resource_app.command("mesh")
def resource_mesh(
    node: str,
    mesh_type: str,
    params: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Create mesh on MeshInstance3D."""
    setup_logging(verbose)
    try:
        call_params = {"node_path": node, "mesh_type": mesh_type}
        if params:
            call_params["mesh_params"] = json.loads(params)
        result = godot_call("scene.create_mesh", call_params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@resource_app.command("light")
def resource_light(
    parent: str,
    light_type: str,
    name: str,
    props: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Create light node."""
    setup_logging(verbose)
    try:
        params = {"parent_path": parent, "light_type": light_type, "name": name}
        if props:
            params["properties"] = json.loads(props)
        result = godot_call("resources.create_light", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@resource_app.command("collision")
def resource_collision(
    node: str,
    shape_type: str,
    params: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Create collision shape."""
    setup_logging(verbose)
    try:
        call_params = {"node_path": node, "shape_type": shape_type}
        if params:
            call_params["shape_params"] = json.loads(params)
        result = godot_call("resources.create_collision_shape", call_params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# FILE COMMANDS
# ============================================================================

file_app = typer.Typer(help="Filesystem operations")
app.add_typer(file_app, name="file")


@file_app.command("search")
def file_search(
    pattern: str,
    path: str = "res://",
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Search files in project."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.search", {"pattern": pattern, "path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@file_app.command("read")
def file_read(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Read file content."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.read_text", {"path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@file_app.command("write")
def file_write(
    path: str,
    content: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Write file content."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.write_text", {"path": path, "content": content})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@file_app.command("mkdir")
def file_mkdir(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Create folder."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.create_folder", {"path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@file_app.command("delete")
def file_delete(
    path: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Delete file or folder."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.delete", {"path": path})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@file_app.command("refresh")
def file_refresh(json_out: JsonOutput = False, verbose: Verbose = False):
    """Refresh filesystem."""
    setup_logging(verbose)
    try:
        result = godot_call("filesystem.refresh")
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# INTROSPECT COMMANDS
# ============================================================================

introspect_app = typer.Typer(help="Introspection and discovery")
app.add_typer(introspect_app, name="introspect")


@introspect_app.command("class")
def introspect_class(
    class_name: str,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Get class properties."""
    setup_logging(verbose)
    try:
        result = godot_call("introspect.class_properties", {"class_name": class_name})
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


@introspect_app.command("catalog")
def introspect_catalog(
    category: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Get class catalog."""
    setup_logging(verbose)
    try:
        params = {"category": category} if category else {}
        result = godot_call("introspect.catalog", params)
        output_result(result, json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# RAW RPC COMMAND
# ============================================================================

@app.command("rpc")
def raw_rpc(
    method: str,
    params: Optional[str] = None,
    json_out: JsonOutput = False,
    verbose: Verbose = False
):
    """Execute raw RPC method (for advanced use)."""
    setup_logging(verbose)
    try:
        call_params = json.loads(params) if params else {}
        result = godot_call(method, call_params)
        output_result(result, json_out)
    except json.JSONDecodeError as e:
        output_error(ValueError(f"Invalid JSON params: {e}"), json_out)
    except Exception as e:
        output_error(e, json_out)


# ============================================================================
# STATUS COMMAND
# ============================================================================

@app.command("status")
def status(json_out: JsonOutput = False, verbose: Verbose = False):
    """Check connection status to Godot."""
    setup_logging(verbose)
    try:
        client = GodotClient()
        if client.connect():
            result = {
                "connected": True,
                "authenticated": client.authenticated,
                "ws_url": client.config.ws_url
            }
            # Get editor info
            try:
                info = client.call("project.get_info")
                result["project"] = info.get("name", "unknown")
            except:
                pass
            client.close()
            output_result(result, json_out)
        else:
            output_result({"connected": False}, json_out)
    except Exception as e:
        output_error(e, json_out)


if __name__ == "__main__":
    app()
