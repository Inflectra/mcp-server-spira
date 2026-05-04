import logging
import os

_default_product_id: int | None = None


def load_config() -> None:
    """Called once at server startup. Reads SPIRA_PROJECT_ID."""
    global _default_product_id
    _default_product_id = None
    raw = os.environ.get("SPIRA_PROJECT_ID")
    if raw is not None:
        try:
            _default_product_id = int(raw)
        except ValueError:
            logging.warning("SPIRA_PROJECT_ID='%s' is not a valid integer, ignoring", raw)


def get_default_product_id() -> int | None:
    return _default_product_id


def resolve_product_id(explicit: int | None) -> int | None:
    """Returns explicit if provided, otherwise the default. May return None."""
    return explicit if explicit is not None else _default_product_id
