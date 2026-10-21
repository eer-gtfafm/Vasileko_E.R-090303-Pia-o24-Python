from interfaces.repository import Repository

# SRP: Отдельный сервис только для генерации отчетов.
class ReportService:
    def __init__(self, room_repo: Repository, booking_repo: Repository):
        self.room_repo = room_repo
        self.booking_repo = booking_repo

    def generate_report(self) -> str:
        rooms = self.room_repo.get_all()
        bookings = self.booking_repo.get_all()
        
        report = "\n--- ОТЧЕТ ПО ГОСТИНИЦЕ ---\n"
        report += f"Всего номеров: {len(rooms)}\n"
        report += f"Свободных номеров: {sum(1 for r in rooms if r.status.value == 'свободен')}\n"
        report += f"Всего бронирований: {len(bookings)}\n"
        report += "Детали бронирований:\n"
        for b in bookings:
            report += f"  - Гость: {b.guest_name}, Номер ID: {b.room_id}, Дней: {b.days}, Стоимость: {b.total_cost} руб.\n"
        return report