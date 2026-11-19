"""Shared fixtures for AgentPilot tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the agentpilot source tree is importable without installing.
_SRC = Path(__file__).resolve().parent.parent / "agentpilot" / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
