import subcompose


def test_remove_subcompose_keys_removes_keys():
    data = {
        "x-subcompose-foo": "bar",
        "keep": "me",
        "nested": {"x-subcompose-bar": "baz", "keep": "me too"},
        "list": [{"x-subcompose-baz": "qux", "keep": "me three"}],
    }
    cleaned = subcompose.remove_subcompose_keys(data)
    assert "x-subcompose-foo" not in cleaned
    assert "keep" in cleaned
    assert "x-subcompose-bar" not in cleaned["nested"]
    assert "keep" in cleaned["nested"]
    assert "x-subcompose-baz" not in cleaned["list"][0]
    assert "keep" in cleaned["list"][0]
