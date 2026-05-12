import pytest
from jarvis.actions.system_cmd import SystemCmd


@pytest.fixture
def cmd():
    return SystemCmd()


def test_system_cmd_init(cmd):
    assert cmd is not None


def test_run_basic_command(cmd):
    result = cmd.run("echo hello")
    assert result["success"] is True
    assert "hello" in result["stdout"]


def test_run_failing_command(cmd):
    result = cmd.run("exit 1")
    assert result["success"] is False


def test_run_powershell(cmd):
    result = cmd.run_powershell("Write-Output 'ps_test'")
    assert result["success"] is True
    assert "ps_test" in result["stdout"]
