from keycloak import KeycloakOpenID


class KeyCloakService:
    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url="http://keycloak:8080/auth",
            client_id="fastapi-client",
            realm_name="fastapi",
            client_secret_key="payrblPE6NuLZbtncDQRvcx2cqDejazK",
        )
        try:
            self.config_well_known = self.keycloak_openid.well_known()
            print("Connected to Keycloak server")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Keycloak server: {e}")

    def get_token(self, username: str, password: str):
        return self.keycloak_openid.token(username, password)

    def get_userinfo(self, access_token: str):
        return self.keycloak_openid.userinfo(access_token)

    def decode_token(self, token: str):
        return self.keycloak_openid.decode_token(token)

    def uma_permissions(self, token: str):
        return self.keycloak_openid.uma_permissions(token)

    def get_roles(self, token: str):
        decoded_token = self.decode_token(token)
        return decoded_token.get("realm_access", {}).get("roles", [])


keycloak_service = KeyCloakService()
