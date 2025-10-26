from keycloak import KeycloakOpenID
from ..common.config import config


class KeyCloakService:
    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=config.KEYCLOAK_SERVER_URL,
            client_id=config.KEYCLOAK_CLIENT_ID,
            realm_name=config.KEYCLOAK_REALM_NAME,
            client_secret_key=config.KEYCLOAK_CLIENT_SECRET_KEY,
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
