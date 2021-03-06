class Technician:

    def __init__(self, technician_dict):
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
        self.guards_per_month = technician_dict["guards_per_month"]
        self.ka_per_month = technician_dict["ka_per_month"]
        self.willing_days = technician_dict["willing_days"] 
        if len(self.willing_days) == 0:
            self.status = "primary"    
        else:
             self.status = "guest"
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
            "days_at_holidays": self.days_at_holidays,
            "guards_per_month": self.guards_per_month,
            "ka_per_month": self.ka_per_month,
            "willing_days": self.willing_days
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
            # Technician has one period of KA in this month
            if -1 not in self.days_at_ka:
                return "ΚΑ", len(self.days_at_ka)
            else: # Technician has more than one period of KA in this month
                start = 0
                try:
                    while True:
                        end = self.days_at_ka.index(-1, start)
                        if day in self.days_at_ka[start:end]:
                            return "ΚΑ", len(self.days_at_ka[start:end])
                        start = end + 1
                except ValueError: # last ka of the month
                    print("into Except")
                    end = len(self.days_at_ka) - 1
                    if day in self.days_at_ka[start:]:
                            return "ΚΑ", len(self.days_at_ka[start:end]) + 1 
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

    def calculate_rest_days_of_ka(self):
        total_ka_days = 30
        self.ka_per_month =[int(ka) for ka in self.ka_per_month]
        return total_ka_days - sum(self.ka_per_month)
    
    def calculate_guest_technician_program(self):
        if len(self.days_at_ka) > 0:
            if -1 not in self.days_at_ka:
                duration = len(self.days_at_ka)
                absence = (self.days_at_ka[0], self.days_at_ka[0] + duration - 1, "ΚΑ")
                self.absence_days.append(absence)
                self.update_technician_program("ΚΑ", self.days_at_ka[0], self.days_at_ka[0] + duration)
            else:
                index = 0
                start = index
                while True:
                    if index == len(self.days_at_ka):
                        break
                    if self.days_at_ka[index] == -1 or index == len(self.days_at_ka)-1:
                        if self.days_at_ka[index] == -1:
                            duration = index - start 
                        else:
                            duration = index - start + 1
                        self.update_technician_program("ΚΑ", self.days_at_ka[start], self.days_at_ka[start] + duration)
                        absence = (self.days_at_ka[start], self.days_at_ka[start] + duration -1, "ΚΑ")
                        self.absence_days.append(absence)
                        start = index + 1 
                    index += 1

        if len(self.days_at_school) > 0:
            duration = len(self.days_at_school)
            self.update_technician_program("ΦΠ", self.days_at_school[0], self.days_at_school[0] + duration)
            absence = (self.days_at_school[0], self.days_at_school[0] + duration, "ΦΠ")
            self.absence_days.append(absence)
        
        if len(self.days_at_hospital) > 0:
            duration = len(self.days_at_hospital)
            self.update_technician_program("ΑΑ", self.days_at_hospital[0], self.days_at_hospital[0] + duration)
            absence = (self.days_at_hospital[0], self.days_at_hospital[0] + duration, "ΑΑ")
            self.absence_days.append(absence)
        
        if len(self.days_at_holidays) > 0:
            duration = len(self.days_at_holidays)
            self.update_technician_program("ΕΑ", self.days_at_holidays[0], self.days_at_holidays[0] + duration)
            absence = (self.days_at_holidays[0], self.days_at_holidays[0] + duration, "ΕΑ")
            self.absence_days.append(absence)


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
