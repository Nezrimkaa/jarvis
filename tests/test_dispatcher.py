import pytest
from jarvis.actions.dispatcher import ActionDispatcher


@pytest.fixture
def dispatcher():
    d = ActionDispatcher()
    d.register("test.echo", lambda i, e, s: e.get("msg", "ok"))
    d.register("test.fail", lambda i, e, s: (_ for _ in ()).throw(Exception("fail")))
    return d


def test_dispatcher_init(dispatcher):
    assert dispatcher is not None


def test_register_and_execute(dispatcher):
    result = dispatcher.execute("test.echo", {"msg": "hello"})
    assert result == "hello"


def test_execute_unknown(dispatcher):
    result = dispatcher.execute("nonexistent", {})
    assert result is None


def test_execute_handler_error(dispatcher):
    result = dispatcher.execute("test.fail", {})
    assert "❌" in result


def test_execute_plan_single(dispatcher):
    results = dispatcher.execute_plan([{"name": "test.echo", "params": {"msg": "hello"}}])
    assert len(results) == 1
    assert results[0] == "hello"


def test_execute_plan_multiple(dispatcher):
    results = dispatcher.execute_plan([
        {"name": "test.echo", "params": {"msg": "first"}},
        {"name": "test.echo", "params": {"msg": "second"}},
    ])
    assert len(results) == 2
    assert results[0] == "first"
    assert results[1] == "second"


def test_execute_plan_error_continues(dispatcher):
    results = dispatcher.execute_plan([
        {"name": "test.echo", "params": {"msg": "ok"}},
        {"name": "test.fail", "params": {}},
        {"name": "test.echo", "params": {"msg": "after"}},
    ])
    assert len(results) == 3
    assert results[0] == "ok"
    assert "❌" in results[1]
    assert results[2] == "after"
