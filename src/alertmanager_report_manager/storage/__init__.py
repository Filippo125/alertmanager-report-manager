"""Storage backends for alert history."""

from alertmanager_report_manager.storage.sqlite import (
    connect,
    initialize_database,
    store_alertmanager_webhook,
)

__all__ = ["connect", "initialize_database", "store_alertmanager_webhook"]
