from typing import Protocol

# Протокол 
class Reportable(Protocol):
    def get_report_data(self) -> str:
        ...