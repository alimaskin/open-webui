from test.util.abstract_integration_test import AbstractPostgresTest
from test.util.mock_user import mock_webui_user
import mock


class TestAuths(AbstractPostgresTest):
    BASE_PATH = "/api/v1/auths"

    def setup_class(cls):
        super().setup_class()
        from open_webui.apps.webui.models.auths import Auths
        from open_webui.apps.webui.models.users import Users

        cls.users = Users
        cls.auths = Auths

    def test_get_session_user(self):
        with mock_webui_user():
            response = self.fast_api_client.get(self.create_url(""))
        assert response.status_code == 200
        assert response.json() == {
            "id": "1",
            "name": "John Doe",
            "email": "john.doe@openwebui.com",
            "role": "user",
            "profile_image_url": "/user.png",
        }

    def test_update_profile(self):
        from open_webui.utils.utils import get_password_hash

        user = self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password=get_password_hash("old_password"),
            name="John Doe",
            profile_image_url="/user.png",
            role="user",
        )

        with mock_webui_user(id=user.id):
            response = self.fast_api_client.post(
                self.create_url("/update/profile"),
                json={"name": "John Doe 2", "profile_image_url": "/user2.png"},
            )
        assert response.status_code == 200
        db_user = self.users.get_user_by_id(user.id)
        assert db_user.name == "John Doe 2"
        assert db_user.profile_image_url == "/user2.png"

    def test_update_password(self):
        from open_webui.utils.utils import get_password_hash

        user = self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password=get_password_hash("old_password"),
            name="John Doe",
            profile_image_url="/user.png",
            role="user",
        )

        with mock_webui_user(id=user.id):
            response = self.fast_api_client.post(
                self.create_url("/update/password"),
                json={"password": "old_password", "new_password": "new_password"},
            )
        assert response.status_code == 200

        old_auth = self.auths.authenticate_user(
            "john.doe@openwebui.com", "old_password"
        )
        assert old_auth is None
        new_auth = self.auths.authenticate_user(
            "john.doe@openwebui.com", "new_password"
        )
        assert new_auth is not None

    def test_signin(self):
        from open_webui.utils.utils import get_password_hash

        user = self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password=get_password_hash("password"),
            name="John Doe",
            profile_image_url="/user.png",
            role="user",
        )
        response = self.fast_api_client.post(
            self.create_url("/signin"),
            json={"email": "john.doe@openwebui.com", "password": "password"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@openwebui.com"
        assert data["role"] == "user"
        assert data["profile_image_url"] == "/user.png"
        assert data["token"] is not None and len(data["token"]) > 0
        assert data["token_type"] == "Bearer"

    def test_signup(self):
        response = self.fast_api_client.post(
            self.create_url("/signup"),
            json={
                "name": "John Doe",
                "email": "john.doe@openwebui.com",
                "password": "password",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None and len(data["id"]) > 0
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@openwebui.com"
        assert data["role"] in ["admin", "user", "pending"]
        assert data["profile_image_url"] == "/user.png"
        assert data["token"] is not None and len(data["token"]) > 0
        assert data["token_type"] == "Bearer"

    def test_add_user(self):
        with mock_webui_user():
            response = self.fast_api_client.post(
                self.create_url("/add"),
                json={
                    "name": "John Doe 2",
                    "email": "john.doe2@openwebui.com",
                    "password": "password2",
                    "role": "admin",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None and len(data["id"]) > 0
        assert data["name"] == "John Doe 2"
        assert data["email"] == "john.doe2@openwebui.com"
        assert data["role"] == "admin"
        assert data["profile_image_url"] == "/user.png"
        assert data["token"] is not None and len(data["token"]) > 0
        assert data["token_type"] == "Bearer"

    def test_get_admin_details(self):
        self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password="password",
            name="John Doe",
            profile_image_url="/user.png",
            role="admin",
        )
        with mock_webui_user():
            response = self.fast_api_client.get(self.create_url("/admin/details"))

        assert response.status_code == 200
        assert response.json() == {
            "name": "John Doe",
            "email": "john.doe@openwebui.com",
        }

    def test_create_api_key_(self):
        user = self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password="password",
            name="John Doe",
            profile_image_url="/user.png",
            role="admin",
        )
        with mock_webui_user(id=user.id):
            response = self.fast_api_client.post(self.create_url("/api_key"))
        assert response.status_code == 200
        data = response.json()
        assert data["api_key"] is not None
        assert len(data["api_key"]) > 0

    def test_delete_api_key(self):
        user = self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password="password",
            name="John Doe",
            profile_image_url="/user.png",
            role="admin",
        )
        self.users.update_user_api_key_by_id(user.id, "abc")
        with mock_webui_user(id=user.id):
            response = self.fast_api_client.delete(self.create_url("/api_key"))
        assert response.status_code == 200
        assert response.json() == True
        db_user = self.users.get_user_by_id(user.id)
        assert db_user.api_key is None

    def test_get_api_key(self):
        user = self.auths.insert_new_auth(
            email="john.doe@openwebui.com",
            password="password",
            name="John Doe",
            profile_image_url="/user.png",
            role="admin",
        )
        self.users.update_user_api_key_by_id(user.id, "abc")
        with mock_webui_user(id=user.id):
            response = self.fast_api_client.get(self.create_url("/api_key"))
        assert response.status_code == 200
        assert response.json() == {"api_key": "abc"}

    def test_oauth_exclusive_mode(self):
        # Mock OAUTH_EXCLUSIVE_AUTH to True
        with mock.patch("open_webui.config.OAUTH_EXCLUSIVE_AUTH.value", True):
            # Test that non-OIDC providers are blocked
            response = self.fast_api_client.get(
                self.create_url("/oauth/google/login")
            )
            assert response.status_code == 404
            
            # Test that OIDC provider works
            response = self.fast_api_client.get(
                self.create_url("/oauth/oidc/login")
            )
            assert response.status_code == 302  # Should redirect to provider
            
            # Test that local auth endpoints are still accessible but return 404
            response = self.fast_api_client.post(
                self.create_url("/signin"),
                json={"email": "test@test.com", "password": "test"}
            )
            assert response.status_code == 404

    def test_oauth_normal_mode(self):
        # Mock OAUTH_EXCLUSIVE_AUTH to False (default behavior)
        with mock.patch("open_webui.config.OAUTH_EXCLUSIVE_AUTH.value", False):
            # Test that all providers work
            for provider in ["google", "microsoft", "oidc"]:
                response = self.fast_api_client.get(
                    self.create_url(f"/oauth/{provider}/login")
                )
                # Should either redirect (if provider configured) or 404 (if not configured)
                assert response.status_code in [302, 404]


class TestOAuthExclusive(AbstractPostgresTest):
    BASE_PATH = "/api/v1/auths"

    def setup_class(cls):
        super().setup_class()
        from open_webui.apps.webui.models.auths import Auths
        from open_webui.apps.webui.models.users import Users
        cls.users = Users
        cls.auths = Auths

    @mock.patch("open_webui.config.OAUTH_EXCLUSIVE_AUTH.value", True)
    def test_local_auth_endpoints_blocked(self):
        # Test that all local auth endpoints return 404
        endpoints = [
            ("/signin", "POST", {"email": "test@test.com", "password": "test"}),
            ("/signup", "POST", {"email": "test@test.com", "password": "test", "name": "Test"}),
            ("/update/password", "POST", {"password": "old", "new_password": "new"}),
            ("/add", "POST", {"email": "test@test.com", "password": "test", "name": "Test", "role": "user"})
        ]
        
        for path, method, data in endpoints:
            response = getattr(self.fast_api_client, method.lower())(
                self.create_url(path),
                json=data
            )
            assert response.status_code == 404, f"Endpoint {path} should return 404 in exclusive mode"

    @mock.patch("open_webui.config.OAUTH_EXCLUSIVE_AUTH.value", True)
    @mock.patch("open_webui.config.ENABLE_OAUTH_ROLE_MANAGEMENT", True)
    def test_oauth_role_management(self):
        # Mock OAuth callback data with roles
        mock_token = {
            "userinfo": {
                "sub": "123",
                "email": "test@test.com",
                "roles": ["admin"],
                "name": "Test User"
            }
        }
        
        with mock.patch("authlib.integrations.starlette_client.OAuth2App.authorize_access_token", 
                       return_value=mock_token):
            response = self.fast_api_client.get(
                self.create_url("/oauth/oidc/callback"),
                params={"code": "test_code", "state": "test_state"}
            )
            
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"  # Role should be taken from OAuth claims
