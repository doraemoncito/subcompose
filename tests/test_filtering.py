# GPL v3 License
# Author: Jose Hernandez

import subcompose
from unittest.mock import patch, MagicMock

def test_filter_by_image_tag_filters_containers():
    parent = {
        "services": {
            "service1": {"container_name": "c1", "image": "img1"},
            "service2": {"container_name": "c2", "image": "img2"},
            "service3": {"container_name": "c3", "image": "img3"},
        }
    }
    service_image_tags = {
        "service1": "tag1",
        "service2": "tag2",
        "service3": None,
    }
    mock_result = MagicMock()
    mock_result.stdout.decode.return_value = "c1"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = mock_result
        result = subcompose.filter_by_image_tag(parent, service_image_tags)
        assert "service1" in result["services"]
        assert "service2" not in result["services"]
        assert "service3" in result["services"]
