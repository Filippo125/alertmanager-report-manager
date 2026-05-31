"""Storage backends for alert history."""

from alertmanager_report_manager.storage.sqlite import connect, initialize_database

__all__ = ["connect", "initialize_database"]
