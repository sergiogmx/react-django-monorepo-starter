from django.db import DatabaseError, connection


class DjangoDatabaseProbe:
    """Implements domain.health.DatabaseProbe with Django's DB connection."""

    def is_available(self) -> bool:
        try:
            connection.ensure_connection()
        except DatabaseError:
            return False
        return True
