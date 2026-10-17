import os

TABLES = ("students", "opportunities", "applications")


class Store:
    """In-memory by default; DynamoDB when USE_DYNAMODB=1."""

    def __init__(self):
        self.mem = {t: {} for t in TABLES}
        self.ddb = None
        if os.getenv("USE_DYNAMODB") == "1":
            import boto3

            self.ddb = boto3.resource(
                "dynamodb", region_name=os.getenv("AWS_REGION", "ap-south-1")
            )

    def _t(self, t):
        return self.ddb.Table(f"SkillPortal-{t}")

    def put(self, t, item):
        if self.ddb:
            self._t(t).put_item(Item=item)
        else:
            self.mem[t][item["id"]] = item

    def get(self, t, key):
        if self.ddb:
            return self._t(t).get_item(Key={"id": key}).get("Item")
        return self.mem[t].get(key)

    def all(self, t):
        if not self.ddb:
            return list(self.mem[t].values())

        table = self._t(t)
        items = []
        response = table.scan()
        items.extend(response.get("Items", []))

        while response.get("LastEvaluatedKey"):
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        return items
