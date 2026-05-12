import pytest
import os
import tempfile
from jarvis.actions.file_ops import FileOperator


@pytest.fixture
def file_op():
    return FileOperator()


@pytest.fixture
def tmp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    import shutil
    shutil.rmtree(dirpath, ignore_errors=True)


def test_create_file(file_op, tmp_dir):
    path = os.path.join(tmp_dir, "test.txt")
    result = file_op.create_file(path)
    assert result is True
    assert os.path.exists(path)


def test_create_file_exists(file_op, tmp_dir):
    path = os.path.join(tmp_dir, "existing.txt")
    open(path, "w").close()
    result = file_op.create_file(path)
    assert result is True  # overwrite


def test_delete_file(file_op, tmp_dir):
    path = os.path.join(tmp_dir, "todelete.txt")
    open(path, "w").close()
    result = file_op.delete_file(path)
    assert result is True
    assert not os.path.exists(path)


def test_delete_nonexistent(file_op, tmp_dir):
    result = file_op.delete_file(os.path.join(tmp_dir, "ghost.txt"))
    assert result is False


def test_create_folder(file_op, tmp_dir):
    path = os.path.join(tmp_dir, "new_folder")
    result = file_op.create_folder(path)
    assert result is True
    assert os.path.isdir(path)


def test_find_files(file_op, tmp_dir):
    open(os.path.join(tmp_dir, "findme.txt"), "w").close()
    results = file_op.find_files("findme", tmp_dir)
    assert len(results) >= 1
