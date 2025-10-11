import os
from pydantic import BaseModel


class Config:
    UPSTREAM_URL: str = os.getenv("UPSTREAM", "http://upstream:81")
    OPA_HOST: str = os.getenv("OPA_HOST", "opa")
    OPA_PORT: int = int(os.getenv("OPA_PORT", 8181))
    OPA_PACKAGE: str = os.getenv("OPA_PACKAGE", "authz")  # rego package
    OPA_RULE: str = os.getenv("OPA_RULE", "allow")


config = Config()
