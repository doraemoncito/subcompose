import pytest
import subcompose
import os
from unittest.mock import patch


def test_substitute_environment_variables_substitutes_vars():
    with patch.dict(os.environ, {"TEST_VAR": "value"}):
        subcompose.substitution.env = os.environ.copy()
        node = {"key": "${TEST_VAR}"}
        result = subcompose.substitute_environment_variables(node)
        assert result["key"] == "value"


def test_substitute_environment_variables_uses_defaults():
    node = {"key": "${NON_EXISTENT:-default}"}
    result = subcompose.substitute_environment_variables(node)
    assert result["key"] == "default"


def test_substitute_environment_variables_ignores_vars():
    with patch.dict(os.environ, {"TEST_VAR": "value"}):
        subcompose.substitution.env = os.environ.copy()
        node = {"key": "${TEST_VAR}"}
        result = subcompose.substitute_environment_variables(
            node, no_interpolate=True, ignored_vars=["TEST_VAR"]
        )
        assert result["key"] == "${TEST_VAR}"


def test_substitute_image_tags_substitutes_tags():
    parent = {
        "services": {
            "service1": {"image": "repo/image:latest"},
            "service2": {"image": "repo/image:old"},
        }
    }
    tags = {"service1": "newtag"}
    result = subcompose.substitute_image_tags(parent, tags)
    assert result["services"]["service1"]["image"] == "repo/image:newtag"
    assert result["services"]["service2"]["image"] == "repo/image:old"


def test_substitute_image_tags_exits_on_missing_image_field():
    parent = {"services": {"service1": {}}}
    tags = {"service1": "newtag"}
    with pytest.raises(SystemExit):
        subcompose.substitute_image_tags(parent, tags)
