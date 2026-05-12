import pytest
import os
import tempfile
from jarvis.actions.git_ops import GitOperator, GitHubOperator


@pytest.fixture
def git_op():
    return GitOperator()


@pytest.fixture
def tmp_repo():
    dirpath = tempfile.mkdtemp()
    os.system(f'cd /d "{dirpath}" && git init && git config user.email "test@test.com" && git config user.name "Test"')
    yield dirpath
    import shutil
    shutil.rmtree(dirpath, ignore_errors=True)


def test_git_operator_init(git_op):
    assert git_op is not None


def test_git_ops_not_git_repo(git_op, tmpdir):
    result = git_op.commit(message="test")
    assert result["success"] is False


def test_github_operator_init():
    gh = GitHubOperator(token="test-token")
    assert gh is not None
