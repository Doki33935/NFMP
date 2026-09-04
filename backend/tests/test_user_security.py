from core.security import verify_password
from models.user import User


def test_password_change_requires_current_password(api_context):
    context = api_context
    client = context["client"]
    inspector = context["roles"]["inspector"]
    context["current"]["user"] = inspector

    body = {
        "new_password": "A-new-strong-password-2026",
        "password_confirmation": "A-new-strong-password-2026",
    }
    assert client.put(f"/users/{inspector.id}/password", json=body).status_code == 400

    body["current_password"] = "Strong-inspector-password-2026"
    response = client.put(f"/users/{inspector.id}/password", json=body)
    assert response.status_code == 200, response.text
    context["db"].refresh(inspector)
    assert verify_password("A-new-strong-password-2026", inspector.password)


def test_admin_user_creation_rejects_weak_password(api_context):
    context = api_context
    context["current"]["user"] = context["roles"]["admin"]
    response = context["client"].post(
        "/users",
        json={
            "username": "new-user",
            "password": "short",
            "password_confirmation": "short",
            "full_name": "New User",
            "role": "dispatcher",
        },
    )
    assert response.status_code == 422
    assert context["db"].query(User).filter(User.username == "new-user").first() is None


def test_plaintext_password_is_never_accepted():
    assert verify_password("legacy-password", "legacy-password") is False


def test_login_uses_http_only_cookie(api_context):
    response = api_context["client"].post(
        "/login",
        json={
            "username": "dispatcher",
            "password": "Strong-dispatcher-password-2026",
        },
    )
    assert response.status_code == 200, response.text
    assert "access_token" not in response.json()
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=strict" in cookie


def test_login_cookie_is_secure_in_production_by_default(api_context, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)

    response = api_context["client"].post(
        "/login",
        json={
            "username": "dispatcher",
            "password": "Strong-dispatcher-password-2026",
        },
    )

    assert response.status_code == 200, response.text
    assert "; Secure" in response.headers["set-cookie"]


def test_login_cookie_can_be_used_on_internal_http(api_context, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")

    response = api_context["client"].post(
        "/login",
        json={
            "username": "dispatcher",
            "password": "Strong-dispatcher-password-2026",
        },
    )

    assert response.status_code == 200, response.text
    assert "; Secure" not in response.headers["set-cookie"]


def test_user_is_disabled_without_deleting_history(api_context):
    context = api_context
    admin = context["roles"]["admin"]
    dispatcher = context["roles"]["dispatcher"]
    context["current"]["user"] = admin

    response = context["client"].delete(f"/users/{dispatcher.id}")
    assert response.status_code == 200
    context["db"].refresh(dispatcher)
    assert dispatcher.disabled_at is not None
    assert context["db"].get(User, dispatcher.id) is dispatcher

    login = context["client"].post(
        "/login",
        json={
            "username": "dispatcher",
            "password": "Strong-dispatcher-password-2026",
        },
    )
    assert login.status_code == 401

    restored = context["client"].post(f"/users/{dispatcher.id}/restore")
    assert restored.status_code == 200
    assert restored.json()["is_active"] is True
