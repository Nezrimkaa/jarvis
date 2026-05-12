import pytest
from unittest.mock import patch
from jarvis.actions.code_editor import CodeEditor


def test_code_editor_init():
    ce = CodeEditor()
    assert ce is not None
    assert len(ce._available_editors) > 0


@patch("subprocess.Popen")
def test_open_file_no_editor(mock_popen):
    ce = CodeEditor()
    result = ce.open_file("test.txt")
    assert result is True
    mock_popen.assert_called_once()
