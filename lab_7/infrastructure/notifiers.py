from interfaces.notifier import Notifier

class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"[EMAIL to {recipient}]: {message}")

class SmsNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"[SMS to {recipient}]: {message}")

class ConsoleNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"[УВЕДОМЛЕНИЕ для {recipient}]: {message}")