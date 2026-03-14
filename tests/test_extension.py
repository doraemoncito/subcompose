import pytest
import subcompose

def test_check_service_extension_chain_detects_circular_dependency():
    parent = {
        "services": {
            "service1": {"extends": {"service": "service2"}},
            "service2": {"extends": {"service": "service1"}},
        }
    }
    with pytest.raises(SystemExit):
        subcompose.check_service_extension_chain(parent, "service1")

def test_check_service_extension_chain_valid_chain():
    parent = {
        "services": {
            "service1": {"extends": {"service": "service2"}},
            "service2": {"image": "base:latest"},
        }
    }
    subcompose.check_service_extension_chain(parent, "service1")

