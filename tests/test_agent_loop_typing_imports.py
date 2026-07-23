"""Regression tests for the annotations on agent_loop's tool-event helpers.

`_resolved_tool_event_name` and `_ody_qwen_terminal_tool_summary` are annotated
`dict[str, Any]`. agent_loop has no `from __future__ import annotations`, so a
missing `Any` import is not a lint nit — the annotation is evaluated when the
`def` runs, which makes importing the module (and therefore starting the app)
raise NameError. py_compile still passes on it, so these tests are what catches
it. Both helpers were otherwise untested.
"""

import typing

import pytest

import src.agent_loop as agent_loop


@pytest.mark.parametrize(
    "func_name",
    ["_resolved_tool_event_name", "_ody_qwen_terminal_tool_summary"],
)
def test_tool_event_helper_annotations_resolve(func_name):
    func = getattr(agent_loop, func_name)
    hints = typing.get_type_hints(func)
    assert hints["return"] is str
    # dict[str, Any] must actually be resolvable against the module globals.
    arg_hint = next(v for k, v in hints.items() if k != "return")
    assert typing.get_origin(arg_hint) is dict


def test_app_entrypoint_imports():
    """app.py is the uvicorn entrypoint; agent_loop is on its import path."""
    import app

    assert app.app is not None


def test_resolved_tool_event_name_returns_plain_tool_name():
    assert agent_loop._resolved_tool_event_name({"tool": "manage_notes"}) == "manage_notes"
    assert agent_loop._resolved_tool_event_name({"tool": "  bash  "}) == "bash"
    assert agent_loop._resolved_tool_event_name({}) == ""


def test_resolved_tool_event_name_digs_mcp_name_out_of_event_fields():
    # An "mcp" event carries the real server/tool name in desc/command/output.
    assert agent_loop._resolved_tool_event_name(
        {"tool": "mcp", "desc": "calling mcp__email__list_emails now"}
    ) == "mcp__email__list_emails"
    assert agent_loop._resolved_tool_event_name(
        {"tool": "mcp", "command": '{"name": "mcp__github__create_issue"}'}
    ) == "mcp__github__create_issue"
    # Nothing to find — fall back to the bare "mcp" label rather than guessing.
    assert agent_loop._resolved_tool_event_name({"tool": "mcp", "desc": "no name here"}) == "mcp"


def test_ody_qwen_terminal_tool_summary_ignores_unrenderable_tools():
    assert agent_loop._ody_qwen_terminal_tool_summary({"tool": "bash", "output": "hi"}) == ""
