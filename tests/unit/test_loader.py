"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish import loader


def test_load_modules_loads_all_files_in_dir(tmp_path, mocker):
    """Load all Python files in a directory."""
    dir_1 = tmp_path / "dir_1"
    dir_1.mkdir()

    dir_2 = tmp_path / "dir_2"
    dir_2.mkdir()

    module1 = dir_1 / "module1.py"
    module2 = dir_2 / "module2.py"
    module1.write_text("""
    from radish import step
    @step("Step 1")
    def step_1():
        pass""")
    module2.write_text("""
    from radish import step
    @step("Step 2")
    def step_2():
        pass""")

    load_module = mocker.patch("radish.loader.load_module")

    loaded_files = set()
    loader.load_modules(str(tmp_path / "dir_1"), loaded_files)
    loader.load_modules(str(tmp_path / "dir_2"), loaded_files)

    assert len(loaded_files) == 2
    assert load_module.call_count == 2


def test_load_modules_skips_identical_files(tmp_path, mocker):
    """Do not load the same module twice through identical files."""
    module = tmp_path / "module.py"
    symlink = tmp_path / "module_alias.py"
    module.write_text(
        """
    from radish import step
    @step("My unique step")
    def my_unique_step():
        pass""",
        encoding="utf-8",
    )

    try:
        symlink.symlink_to(module, target_is_directory=False)
    except (OSError, NotImplementedError) as error:
        pytest.skip("creating symlinks is not supported: {}".format(error))

    load_module = mocker.patch("radish.loader.load_module")

    loader.load_modules(str(tmp_path))

    load_module.assert_called_once()


def test_load_modules_skips_loaded_files(tmp_path, mocker):
    """Do not load the same module twice through already loaded files."""
    module = tmp_path / "module.py"
    module.write_text("""
    from radish import step
    @step("My unique step")
    def my_unique_step():
        pass""")

    load_module = mocker.patch("radish.loader.load_module")

    loaded_files = set()
    loader.load_modules(str(tmp_path), loaded_files)
    loader.load_modules(str(tmp_path), loaded_files)

    load_module.assert_called_once()
