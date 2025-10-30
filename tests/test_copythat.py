import pytest
import sys
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
import copythat

def test_copythat(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "file.txt").write_text("hello")
    copythat.shutil.copytree(str(src), str(dst))
    assert (dst / "file.txt").read_text() == "hello"
