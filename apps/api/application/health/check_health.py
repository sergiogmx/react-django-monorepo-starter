from domain.health import ComponentStatus, DatabaseProbe, HealthReport


class CheckHealth:
    """Use case: report whether the API's dependencies are available."""

    def __init__(self, database: DatabaseProbe) -> None:
        self._database = database

    def execute(self) -> HealthReport:
        available = self._database.is_available()
        return HealthReport(
            database=ComponentStatus.UP if available else ComponentStatus.DOWN
        )
