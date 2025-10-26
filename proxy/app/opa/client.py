from opa_client.opa import OpaClient
from ..common.config import config


class OPAService:
    def __init__(self):
        print(config.OPA_HOST, config.OPA_PORT)
        self.client = OpaClient(host=config.OPA_HOST, port=config.OPA_PORT)
        if not self.check_connection():
            raise ConnectionError("Failed to connect to OPA server")
        else:
            print("Connected to OPA server")

        # self.update_policy_from_file(
        #     filepath="/app/app/opa/policies/api.rego",
        #     endpoint="authz",
        # )

    def check_connection(self):
        try:
            return self.client.check_connection()  # True
        finally:
            self.client.close_connection()

    def update_policy_from_file(self, filepath, endpoint):
        self.client.update_policy_from_file(filepath=filepath, endpoint=endpoint)

    def is_allowed(self, input_data):
        result = self.client.query_rule(
            input_data=input_data,
            package_path="authz",
            rule_name="allow",
        )
        return result.get("result", False)


opa_client = OPAService()
