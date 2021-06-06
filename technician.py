class Technician:
    ''''ΤΑ IF ΔΕΝ ΧΡΕΙΑΖΟΝΤΑΙ ΟΠΩΣ ΚΑΙ ΤΑ ATTRIBUTES ΣΤΟΝ CONSTRUCTOR'''
    def __init__(self, tech_id="", name="", surname="", specialty="", grade="", letter="",
                 ka=None, school=None, holidays=None, hospital=None, program=None):
        self.tech_id = tech_id
        self.name = name
        self.surname = surname
        self.specialty = specialty
        self.grade = grade
        self.letter = letter
        if ka is None:
            self.days_at_ka = []
        else:
            self.days_at_ka = ka
        if school is None:
            self.days_at_school = []
        else:
            self.days_at_school = school
        if holidays is None:
            self.days_at_holidays = []
        else:
            self.days_at_holidays = holidays
        if hospital is None:
            self.days_at_hospital = []
        else:
            self.days_at_hospital = hospital
        if program is None:
            self.technician_program = ["off" for _ in range(32)]
        else:
            self.technician_program = program
        self.absence_days = []

    def from_dict(self, technician_dict):
        self.tech_id = technician_dict["tech_id"]
        self.name = technician_dict["name"]
        self.surname = technician_dict["surname"]
        self.specialty = technician_dict["specialty"]
        self.grade = technician_dict["grade"]
        self.letter = technician_dict["letter"]
        self.days_at_ka = technician_dict["days_at_ka"]
        self.days_at_school = technician_dict["days_at_school"]
        self.days_at_hospital = technician_dict["days_at_hospital"]
        self.days_at_holidays = technician_dict["days_at_holidays"]
        self.technician_program = ["off" for _ in range(32)]
        self.absence_days = []

    def to_dict(self):
        technician_dict = {
            "tech_id": self.tech_id,
            "name": self.name,
            "surname": self.surname,
            "specialty": self.specialty,
            "grade": self.grade,
            "letter": self.letter,
            "days_at_ka": self.days_at_ka,
            "days_at_school": self.days_at_school,
            "days_at_hospital": self.days_at_hospital,
            "days_at_holidays": self.days_at_holidays
        }
        return technician_dict

    def is_available(self, day):
        return day not in self.days_at_ka and day not in self.days_at_school and \
               day not in self.days_at_hospital and day not in self.days_at_holidays

    def has_kind_of_holidays(self):
        for i in ("ΚΑ", "ΑΑ", "ΕΑ", "ΦΠ"):
            if i in self.technician_program:
                return True

    def update_technician_program(self, status, from_day, to_day=None):
        if to_day is not None:
            for day in range(from_day, to_day):
                if day < len(self.technician_program):
                    self.technician_program[day] = status
        else:
            self.technician_program[from_day] = status

    def __reason_of_absence(self, day):
        '''Έλεγχος αν κάποιος θέλει να πάρει άδεια 2 φορές στον ίδιο μήνα'''
        if day in self.days_at_ka:
            return "ΚΑ", len(self.days_at_ka)
        elif day in self.days_at_school:
            return "ΦΠ", len(self.days_at_school)
        elif day in self.days_at_holidays:
            return "ΕΑ", len(self.days_at_holidays)
        elif day in self.days_at_hospital:
            return "ΑΑ", len(self.days_at_hospital)


    def calculate_next_guard(self, day):
        reason, days_of_absence = self.__reason_of_absence(day)
        if reason == "ΦΠ":
            absence_from = self.days_at_school[0]
            absence = (absence_from, absence_from + days_of_absence - 1, reason)
            self.absence_days.append(absence)
            return reason, absence_from, absence_from + days_of_absence
        if reason == "ΑΑ":
            absence_from = self.days_at_hospital[0]
            absence = (absence_from, absence_from + days_of_absence - 1, reason)
            self.absence_days.append(absence)
            return reason, absence_from, absence_from + days_of_absence
        else:
            absence_from = day
            absence_to = day + days_of_absence - 1
            next_guard = absence_to + 1
            absence = (day, absence_to, reason)
            self.absence_days.append(absence)
            return reason, absence_from, next_guard

    def __str__(self):
        return f"{self.grade} ({self.specialty}) {self.surname} {self.name}"

    def __repr__(self):
        string = f"{self.tech_id} {self.letter} {self.grade} ({self.specialty}) {self.surname} {self.name}\n"
        if not self.days_at_ka:
            string += "Δεν επιθυμεί κανονική άδεια\n"
        else:
            string += f"Επιθυμεί {len(self.days_at_ka)} ΚΑ τις ακόλουθες ημέρες: "
            for day in self.days_at_ka:
                string += f"{day} "
            string += "\n"
        return string
