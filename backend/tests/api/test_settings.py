from app.core import constants


def test_provider_settings_roundtrip_masks_api_key(client) -> None:
    empty = client.get(constants.API_SETTINGS_PROVIDER_PATH)
    assert empty.status_code == 200
    assert empty.json()["api_key_configured"] is False

    saved = client.put(
        constants.API_SETTINGS_PROVIDER_PATH,
        json={
            "base_url": "https://example.com/v1",
            "model_name": "demo-model",
            "api_key": "secret-key",
        },
    )
    assert saved.status_code == 200
    body = saved.json()
    assert body["base_url"] == "https://example.com/v1"
    assert body["model_name"] == "demo-model"
    assert body["api_key_configured"] is True
    assert "secret-key" not in body.values()
