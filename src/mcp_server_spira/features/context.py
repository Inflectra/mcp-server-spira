import logging

from mcp_server_spira.config import get_default_product_id
from mcp_server_spira.utils.spira_client import get_client

_active_product_context: dict | None = None


async def load_active_product_context() -> None:
    """Fetches product details and active releases. Called once in lifespan.

    Spec:
        - NEVER raises — catches all exceptions and logs a warning
        - When SPIRA_PROJECT_ID env is unset (get_default_product_id
          returns None): returns immediately without any API calls,
          leaving _active_product_context as None
        - On success: sets _active_product_context to a dict with keys
          product_id (int), name (str|None), description (str|None),
          active_releases (list of dicts with ReleaseId, Name,
          VersionNumber)
        - active_releases filters to releases where Active is not False
          (missing Active field treated as True — permissive)
        - Makes exactly 2 API calls: GET projects/{id} and POST
          projects/{id}/releases/search with empty body
        - Called once during server lifespan startup — not called per
          request
    """
    global _active_product_context
    product_id = get_default_product_id()
    if product_id is None:
        return
    try:
        client = get_client()
        product = await client.make_spira_api_get_request(f"projects/{product_id}")
        releases = await client.make_spira_api_post_request(
            f"projects/{product_id}/releases/search", {}
        )
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
