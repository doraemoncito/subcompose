import subcompose


def test_validate_volumes_detects_unused_volumes():
    data = {
        "services": {"service1": {"volumes": ["used_vol:/data"]}},
        "volumes": {"used_vol": {}, "unused_vol": {}},
    }
    issues, fixed = subcompose.validate_volumes(data, fix=False)
    assert issues is True
    assert fixed is False


def test_validate_volumes_fixes_unused_volumes():
    data = {
        "services": {"service1": {"volumes": ["used_vol:/data"]}},
        "volumes": {"used_vol": {}, "unused_vol": {}},
    }
    issues, fixed = subcompose.validate_volumes(data, fix=True)
    assert issues is True
    assert fixed is True
    assert "unused_vol" not in data["volumes"]
    assert "used_vol" in data["volumes"]
