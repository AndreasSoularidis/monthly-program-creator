import calendar
from day import Day
from technician import Technician


class Program:

    def __init__(self, program_data_dict, technicians):
        self.technicians = technicians
        self.full_program = bool(program_data_dict["full_program"])
        self.number_of_technicians = program_data_dict["number_of_technicians"]
        self.active_technicians = program_data_dict["active_technicians"]
        self.month = program_data_dict["month"]
        self.year = program_data_dict["year"]
        self.first_day_of_month, self.days_of_month = calendar.monthrange(self.year, self.month)
        self.days_of_month += 1
        self.sequence = program_data_dict["sequence"]

        if self.number_of_technicians - self.active_technicians >= 1:
            self.technicians_out_of_order = program_data_dict["technicians_out_of_order"]
        else:
            self.technicians_out_of_order = []

        if not self.full_program:
            self.empty_slots = program_data_dict["empty_slots"]
        else:
            self.empty_slots = []

        self.next_month_out_of_order_technicians = []
        self.guards_program = []

        if self.month == 1:
            for technician in self.technicians:
                technician.previous_years_ka = sum(technician.ka_per_month)
                technician.ka_per_month = []
                technician.guards_per_month = []

    def initialization(self):
        day = self.first_day_of_month
        for guard_day in range(self.days_of_month):
            if guard_day == 0:
                self.guards_program.append(Day(guard_day, 0, "-"))
            else:
                self.guards_program.append(Day(guard_day, day, "-"))
                day += 1
                if day == 7:
                    day = 0

    def next_available_day(self, day):
        while self.guards_program[day].date < self.days_of_month:
            if self.guards_program[day].technician_id == "-":
                return day
            day += 1


    def __next_technician(self, technician_id):
        for technician in self.technicians:
            if technician.tech_id == technician_id:
                return technician

    def find_next_technician(self, day):
        counter = 0
        while True:
            if counter == self.active_technicians:
                return self.__next_technician(self.guards_program[day].technician_id)
            day -= 1
            if self.guards_program[day].technician_id != "/":
                counter += 1

    def day_is_empty(self, day):
        if self.guards_program[day].technician_id == "-":
            return True
        return False

    def day_must_be_empty(self, day):
        if self.guards_program[day].technician_id == "/":
            return True
        return False

    def day_has_technician(self, day):
        if not self.day_is_empty(day) and not self.day_must_be_empty(day):
            return True
        return False

    def has_technicians_out_of_order(self):
        return len(self.technicians_out_of_order)

    def set_empty_days(self):
        for day in self.empty_slots:
            self.guards_program[day].technician_id = "/"

    def find_technician_by_id(self, technician_id):
        for technician in self.technicians:
            if technician_id == technician.tech_id:
                return technician
        return None

    def add_technician_to_next_month(self, technician_id, day, next_guard, reason):
        technician_dict = {
            "technician_id": technician_id,
            "from_day": day,
            "first_guard": next_guard,
            "month_days": self.days_of_month,
            "reason": reason
        }
        self.next_month_out_of_order_technicians.append(technician_dict)

    def calculate_number_of_guards(self):
        for technician in self.technicians:
            counter = 0
            for day in technician.technician_program:
                if day == "ΥΠ":
                    counter += 1
            technician.guards_per_month.append(counter)
    
    def calculate_ka_days(self):
        for technician in self.technicians:
            counter = 0
            for day in technician.technician_program:
                if day == "ΚΑ":
                    counter += 1
            technician.ka_per_month.append(counter)


    def __repr__(self):
        program = f"Full program: {self.full_program}\n"
        program += f"Number of technicians: {self.number_of_technicians}\n"
        program += f"Active technicians: {self.active_technicians}\n"
        program += f"Month: {self.month} Year: {self.year}\n"
        program += f"Days of month: {self.days_of_month} First day of month: {self.first_day_of_month}\n"
        program += f"Sequence {self.sequence}\n"
        program += f"Technicians out of order: {self.technicians_out_of_order}\n"
        program += f"Empty slots: {self.empty_slots}"
        return program

    def __str__(self):
        program = ""
        program += f"ΠΡΟΓΡΑΜΜΑ {str(self.month).zfill(2)}/{self.year}\n"
        program += "\n"
        for day in self.guards_program:
            if day.date == 0:
                continue
            program += f"{str(day.date).zfill(2)} "
        program += "\n"

        for i in range(1, len(self.guards_program)):
            program += f"{self.guards_program[i].day} "
        program += "\n"

        for i in range(1, len(self.guards_program)):
            tech = self.guards_program[i].technician_id
            for technician in self.technicians:
                if technician.tech_id == self.guards_program[i].technician_id:
                    tech = technician.letter
                    break
            program += f"{tech}  "

        program += "\n\nΆδειες\n\n"
        for technician in self.technicians:
            if technician.has_kind_of_holidays():
                program += f"{technician.grade} ({technician.specialty}) {technician.surname} {technician.name} "
                for tech_out_of_order in self.technicians_out_of_order:
                    if tech_out_of_order["technician_id"] == technician.tech_id:
                        program += f"{tech_out_of_order['month_days'] + tech_out_of_order['first_guard'] - tech_out_of_order['from_day']}{tech_out_of_order['reason']} "
                        program += f"από {tech_out_of_order['from_day']}/{self.month - 1} "
                        program += f"έως {tech_out_of_order['first_guard'] - 1}/{self.month}, "
                        break
                for absence in range(len(technician.absence_days)):
                    from_day = technician.absence_days[absence][0]
                    to_day = technician.absence_days[absence][1]
                    reason = technician.absence_days[absence][2]
                    program += f"{to_day - from_day + 1}{reason} "
                    program += f"από {from_day}/{self.month} "
                    if to_day >= self.days_of_month:
                        program += f"έως {to_day - self.days_of_month + 1}/{self.month + 1}"
                    else:
                        program += f"έως {to_day}/{self.month}"
                    if absence == len(technician.absence_days) - 1:
                        program += "."
                    else:
                        program += ", "
                program += "\n"
        program += "\n\nΣτατιστικά Στοιχεία\n\n"
        program += f"{'Τεχνικός':<30}{'Τρέχων Μήνας':<15}{'Σύνολο Υπηρεσιών':<20}{'Υπόλοιπο Κανονικής Άδειας':<20}\n"
        for technician in self.technicians:
            program += f"{technician.grade + ' (' + technician.specialty + ') ' + technician.surname + ' ' + technician.name[0] + '.':<36}{technician.guards_per_month[-1]:<15}{sum(technician.guards_per_month):<25}{technician.calculate_rest_days_of_ka()}\n"
        return program

    def store_program(self):
        with open("program.txt", "w", encoding="utf-8") as f:
            f.write(self.__str__())
