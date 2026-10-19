import logging
import os

_default_product_id: int | None = None
_create_tags: str | None = None
_update_tags: str | None = None


def load_config() -> None:
    """Called once at server startup.

    Reads SPIRA_PROJECT_ID, SPIRA_CREATE_TAGS, and SPIRA_UPDATE_TAGS.
    """
    global _default_product_id, _create_tags, _update_tags
    _default_product_id = None
    raw = os.environ.get("SPIRA_PROJECT_ID")
    if raw is not None:
        try:
            _default_product_id = int(raw)
        except ValueError:
            logging.warning("SPIRA_PROJECT_ID='%s' is not a valid integer, ignoring", raw)

    # Normalize each tags var exactly once and independently of the other.
    _create_tags = _normalize_tags_env(os.environ.get("SPIRA_CREATE_TAGS"))
    _update_tags = _normalize_tags_env(os.environ.get("SPIRA_UPDATE_TAGS"))


def _normalize_tags_env(raw: str | None) -> str | None:
    """Normalize a tags env value to a non-empty string or the disabled sentinel.

    Spec:
        - Absent (None), empty, or whitespace-only input returns None, the
          disabled sentinel indicating injection is off for that env var
        - Otherwise returns the value with leading/trailing whitespace removed,
          which is guaranteed non-empty
        - Pure value transformation; never raises, no side effects
    """
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped or None


def get_default_product_id() -> int | None:
    return _default_product_id


def get_create_tags() -> str | None:
    """Return the normalized SPIRA_CREATE_TAGS value computed at load_config time.

    Spec:
        - Returns exactly one of two forms: a non-empty whitespace-trimmed
          string (create injection enabled), or None (the disabled sentinel)
        - Reflects the value snapshotted during the last load_config() run;
          environment changes after load_config() are not observed until
          load_config() runs again
        - Never raises — plain accessor over the module global
    """
    return _create_tags


def get_update_tags() -> str | None:
    """Return the normalized SPIRA_UPDATE_TAGS value computed at load_config time.

    Spec:
        - Returns exactly one of two forms: a non-empty whitespace-trimmed
          string (update injection enabled), or None (the disabled sentinel)
        - Reflects the value snapshotted during the last load_config() run;
          environment changes after load_config() are not observed until
          load_config() runs again
        - Never raises — plain accessor over the module global
    """
    return _update_tags


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
