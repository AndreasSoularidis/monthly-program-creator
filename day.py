class Day:
    def __init__(self, date="", day="", technician_id=""):
        self.date = date
        self.day = self.day_of_the_week(day)
        self.technician_id = technician_id

    def day_of_the_week(self, day):
        days = {
            0: "Δε",
            1: "Τρ",
            2: "Τε",
            3: "Πε",
            4: "Πα",
            5: "Σα",
            6: "Κυ"
        }
        return days[day]

    def print_date(self):
        print(self.date, end="")

    def __str__(self):
        day = f"{str(self.date).zfill(2)}"
        day += f"{self.day}"
        day += f"{self.technician_id} "
        return day