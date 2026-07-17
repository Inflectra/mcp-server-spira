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
    """Returns explicit if provided, otherwise the default. May return None.

    Spec:
        - When explicit is not None, ALWAYS returns explicit — the env default
          is never consulted (explicit=0 is valid, not treated as falsy)
        - When explicit is None, returns the module-level _default_product_id
          (which may itself be None if SPIRA_PROJECT_ID was absent or invalid)
        - Never raises — pure value selection with no side effects
        - Callers (product tools, automation tools) check the return value for
          None and produce an INVALID_PARAMETER error envelope when both
          explicit and default are unset — this function does NOT produce
          error messages itself
    """
    return explicit if explicit is not None else _default_product_id
