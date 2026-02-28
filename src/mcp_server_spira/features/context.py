import logging

from mcp_server_spira.config import get_default_product_id
from mcp_server_spira.utils.spira_client import get_client

_active_product_context: dict | None = None


async def load_active_product_context() -> None:
    """Fetches product details and active releases. Called once in lifespan."""
    global _active_product_context
    product_id = get_default_product_id()
    if product_id is None:
        return
    try:
        client = get_client()
        product = client.make_spira_api_get_request(f"projects/{product_id}")
        releases = client.make_spira_api_post_request(f"projects/{product_id}/releases/search", {})
        active_releases = [
            {
                "ReleaseId": r["ReleaseId"],
                "Name": r["Name"],
                "VersionNumber": r["VersionNumber"],
            }
            for r in releases
            if r.get("Active", True)
        ]
        _active_product_context = {
            "product_id": product_id,
            "name": product.get("Name"),
            "description": product.get("Description"),
            "active_releases": active_releases,
        }
    except Exception as e:
        logging.warning("Failed to load active product context: %s", e)


def get_active_product_context() -> dict | None:
    return _active_product_context
