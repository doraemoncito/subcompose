import subcompose

def test_remove_dependencies_from_filtered_containers_removes_deps():
    parent = {"services": {"service1": {"depends_on": ["service2", "service3"]}}}
    groups = {"all": ["service1", "service2"], "managed": []}
    result = subcompose.remove_dependencies_from_filtered_containers(parent, groups)
    assert "depends_on" not in result["services"]["service1"]

def test_remove_dependencies_from_filtered_containers_managed():
    parent = {
        "services": {
            "service1": {"depends_on": ["service2", "external_service"]},
            "service2": {"x-subcompose-managed": True},
            "external_service": {},
        }
    }
    groups = {"all": ["service1", "service2"], "managed": []}
    result = subcompose.remove_dependencies_from_filtered_containers(
        parent, groups, only_managed=True
    )
    assert "service2" not in result["services"]["service1"]["depends_on"]
    assert "external_service" in result["services"]["service1"]["depends_on"]

