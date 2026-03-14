# GPL v3 License
# Author: Jose Hernandez

import subcompose

def test_get_groups_from_data_extracts_groups_correctly():
    data = {
        "services": {
            "service1": {"x-subcompose-groups": ["group1"]},
            "service2": {"x-subcompose-groups": ["group1", "group2"]},
            "service3": {},
        }
    }
    groups = subcompose.get_groups_from_data(data)
    assert "group1" in groups
    assert "group2" in groups
    assert "all" in groups
    assert "service1" in groups["group1"]
    assert "service2" in groups["group1"]
    assert "service2" in groups["group2"]
    assert "service3" in groups["all"]

def test_get_groups_from_data_handles_empty_data():
    groups = subcompose.get_groups_from_data({})
    assert groups == {}

def test_get_groups_from_data_handles_none():
    groups = subcompose.get_groups_from_data(None)
    assert groups == {}
