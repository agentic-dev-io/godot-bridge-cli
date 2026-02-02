# Godot Bridge CLI

Unified CLI tool for Godot Editor control via WebSocket.

## Installation

```bash
uv tool install /path/to/godot-bridge-cli
```

## Configuration

Set environment variables:
- `GODOT_WS_URL` - WebSocket URL (default: ws://127.0.0.1:49631)
- `GODOT_TOKEN` - Authentication token
- `GODOT_TOKEN_FILE` - Path to token file

## Usage

```bash
# Check connection
godot-bridge status

# Scene operations
godot-bridge scene create Node3D res://scenes/level.tscn
godot-bridge scene open res://scenes/main.tscn
godot-bridge scene tree

# Node operations
godot-bridge node add Player CharacterBody3D Player
godot-bridge node set Player '{"position": {"x": 0, "y": 1, "z": 0}}'
godot-bridge node list

# Script operations
godot-bridge script write res://scripts/player.gd --file ./player.gd
godot-bridge script assign Player res://scripts/player.gd

# Run game
godot-bridge play run
godot-bridge play stop

# Raw RPC (advanced)
godot-bridge rpc auth.ping
```

## JSON Output

Use `--json` flag for machine-readable output:

```bash
godot-bridge scene tree --json
```
