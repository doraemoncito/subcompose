# GPL v3 License
# Author: Jose Hernandez

import subcompose
from unittest.mock import patch


def get_default_args():
    return {
        "--list": False,
        "run": False,
        "stop": False,
        "delete-containers": False,
        "delete-images": False,
        "preview": False,
        "validate": False,
        "--fix": False,
        "--compose-file": "compose.yaml",
        "--debug": False,
        "--interpolate": False,
        "--service": [],
        "--group": [],
        "--src-tag": None,
        "--all": False,
        "--registry": None,
        "--dst-tag": None,
        "--env-var": [],
        "--var-file": None,
        "pull": False,
        "push": False,
        "tag": False,
        "--unmanaged": False,
    }


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("sys.argv", ["subcompose.py", "--list"])
def test_main_list(mock_read_text, mock_docopt, capsys):
    mock_read_text.return_value = """
services:
  service1:
    x-subcompose-groups: [group1]
  service2:
    x-subcompose-groups: [group1]
"""
    args = get_default_args()
    args["--list"] = True
    mock_docopt.return_value = args
    subcompose.main()
    captured = capsys.readouterr()
    assert "[group1]" in captured.out
    assert "service1" in captured.out
    assert "service2" in captured.out


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("subprocess.run")
@patch("sys.argv", ["subcompose.py", "run", "--group=group1"])
def test_main_run(mock_run, mock_read_text, mock_docopt):
    mock_read_text.return_value = """
services:
  service1:
    image: img1
    x-subcompose-groups: [group1]
"""
    args = get_default_args()
    args["run"] = True
    args["--group"] = ["group1"]
    mock_docopt.return_value = args
    subcompose.main()
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert "docker compose" in args[0]
    assert "up -d" in args[0]
    assert "service1" in kwargs["input"]


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("subprocess.run")
@patch("sys.argv", ["subcompose.py", "stop", "--group=group1"])
def test_main_stop(mock_run, mock_read_text, mock_docopt):
    mock_read_text.return_value = """
services:
  service1:
    image: img1
    x-subcompose-groups: [group1]
"""
    args = get_default_args()
    args["stop"] = True
    args["--group"] = ["group1"]
    mock_docopt.return_value = args
    with patch("subcompose.cli.filter_by_image_tag") as mock_filter:
        mock_filter.side_effect = lambda parent, tags: parent
        subcompose.main()
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert "docker compose" in args[0]
    assert "stop" in args[0]


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("subprocess.run")
@patch("sys.argv", ["subcompose.py", "delete-containers", "--group=group1"])
def test_main_delete_containers(mock_run, mock_read_text, mock_docopt):
    mock_read_text.return_value = """
services:
  service1:
    image: img1
    x-subcompose-groups: [group1]
"""
    args = get_default_args()
    args["delete-containers"] = True
    args["--group"] = ["group1"]
    mock_docopt.return_value = args
    with patch("subcompose.cli.filter_by_image_tag") as mock_filter:
        mock_filter.side_effect = lambda parent, tags: parent
        subcompose.main()
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert "docker compose" in args[0]
    assert "rm --force --stop" in args[0]


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("subprocess.run")
@patch("sys.argv", ["subcompose.py", "delete-images", "--group=group1"])
def test_main_delete_images(mock_run, mock_read_text, mock_docopt):
    mock_read_text.return_value = """
services:
  service1:
    image: img1
    x-subcompose-groups: [group1]
"""
    args = get_default_args()
    args["delete-images"] = True
    args["--group"] = ["group1"]
    mock_docopt.return_value = args
    with patch("subcompose.cli.filter_by_image_tag") as mock_filter:
        mock_filter.side_effect = lambda parent, tags: parent
        subcompose.main()
    assert mock_run.call_count == 2
    args1, _ = mock_run.call_args_list[0]
    assert "rm --force --stop" in args1[0]
    args2, _ = mock_run.call_args_list[1]
    assert "docker rmi" in args2[0]
    assert "img1" in args2[0]


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("sys.argv", ["subcompose.py", "preview", "--group=group1"])
def test_main_preview(mock_read_text, mock_docopt, capsys):
    mock_read_text.return_value = """
services:
  service1:
    image: img1
    x-subcompose-groups: [group1]
"""
    args = get_default_args()
    args["preview"] = True
    args["--group"] = ["group1"]
    mock_docopt.return_value = args
    subcompose.main()
    captured = capsys.readouterr()
    assert "service1" in captured.out
    assert "img1" in captured.out


@patch("subcompose.cli.docopt")
@patch("pathlib.Path.read_text")
@patch("sys.argv", ["subcompose.py", "validate"])
def test_main_validate(mock_read_text, mock_docopt):
    mock_read_text.return_value = """
services:
  service1:
    image: img1
"""
    args = get_default_args()
    args["validate"] = True
    mock_docopt.return_value = args
    with (
        patch("subcompose.cli.validate_groups") as mock_val_groups,
        patch("subcompose.cli.validate_volumes") as mock_val_volumes,
    ):
        mock_val_groups.return_value = (False, False)
        mock_val_volumes.return_value = (False, False)
        subcompose.main()
        mock_val_groups.assert_called_once()
        mock_val_volumes.assert_called_once()
