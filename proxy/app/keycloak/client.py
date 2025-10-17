from keycloak import KeycloakOpenID


class KeyCloakService:
    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url="http://keycloak:8080",
            client_id="PGT",
            realm_name="PGT",
            client_secret_key="km7whmkbJLCFMIk5OmfVtjlKasR4ZwL9",
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
    
    def get_auth_url(self, redirect_uri: str, state: str | None = None) -> str:
        return self.keycloak_openid.auth_url(redirect_uri=redirect_uri, state=state)
keycloak_service = KeyCloakService()
