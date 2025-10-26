import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Config:
    UPSTREAM_URL: str = os.getenv("UPSTREAM_URL")

    OPA_HOST: str = os.getenv("OPA_HOST")
    OPA_PORT: int = int(os.getenv("OPA_PORT", 8181))
    OPA_PACKAGE: str = os.getenv("OPA_PACKAGE", "authz")  # rego package
    OPA_RULE: str = os.getenv("OPA_RULE", "allow")

    KEYCLOAK_SERVER_URL: str = os.getenv(
        "KEYCLOAK_SERVER_URL", "http://keycloak:8080/auth"
    )
    KEYCLOAK_REALM_NAME: str = os.getenv("KEYCLOAK_REALM_NAME", "fastapi")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "fastapi-client")
    KEYCLOAK_CLIENT_SECRET_KEY: str = os.getenv(
        "KEYCLOAK_CLIENT_SECRET_KEY", "payrblPE6NuLZbtncDQRvcx2cqDejazK"
    )


config = Config()
