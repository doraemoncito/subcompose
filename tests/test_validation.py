import subcompose


def test_validate_groups_detects_undefined_groups():
    groups = {"undefined_group": ["service1"], "all": ["service1"]}
    data = {"services": {"service1": {}}, "x-subcompose-groups": {}}
    issues, fixed = subcompose.validate_groups(groups, data, fix=False)
    assert issues is True
    assert fixed is False


def test_validate_groups_fixes_undefined_groups():
    groups = {"undefined_group": ["service1"], "all": ["service1"]}
    data = {"services": {"service1": {}}, "x-subcompose-groups": {}}
    issues, fixed = subcompose.validate_groups(groups, data, fix=True)
    assert issues is True
    assert fixed is True
    assert "undefined_group" in data["x-subcompose-groups"]


def test_validate_groups_detects_empty_defined_groups():
    groups = {"all": []}
    data = {"services": {}, "x-subcompose-groups": {"empty_group": {}}}
    issues, fixed = subcompose.validate_groups(groups, data, fix=False)
    assert issues is True
    assert fixed is False


def test_validate_groups_fixes_empty_defined_groups():
    groups = {"all": []}
    data = {"services": {}, "x-subcompose-groups": {"empty_group": {}}}
    issues, fixed = subcompose.validate_groups(groups, data, fix=True)
    assert issues is True
    assert fixed is True
    assert "empty_group" not in data["x-subcompose-groups"]


def test_validate_groups_detects_missing_dependencies():
    groups = {"group1": ["service1"], "all": ["service1", "service2"]}
    data = {"services": {"service1": {"depends_on": ["service2"]}, "service2": {}}}
    issues, fixed = subcompose.validate_groups(groups, data, fix=False)
    assert issues is True
    assert fixed is False


def test_validate_groups_fixes_missing_dependencies():
    groups = {"group1": ["service1"], "all": ["service1", "service2"]}
    data = {
        "services": {
            "service1": {"depends_on": ["service2"]},
            "service2": {"image": "busybox"},
        },
        "x-subcompose-groups": {"group1": {}},
    }
    issues, fixed = subcompose.validate_groups(groups, data, fix=True)
    assert issues is True
    assert fixed is True
    assert "group1" in data["services"]["service2"]["x-subcompose-groups"]
