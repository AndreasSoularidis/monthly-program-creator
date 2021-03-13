import json
from program import Program
from technician import Technician

''' Θα πρέπει το πρόγραμμα όταν δημιουργεί τη σειρά για τον επόμενο μήνα
να μην λαμβάνει υπόψη στη σειρά τυχόν κενές ημέρες'''


def read_technicians_data(file):
    technicians = []
    try:
        with open(file, encoding="utf-8") as f:
            technicians_list_dict = json.load(f)

        for technician in technicians_list_dict:
            new_technician = Technician()
            new_technician.from_dict(technician)
            technicians.append(new_technician)
    except FileNotFoundError:
        raise Exception("Fatal Error! Technicians Data file not found.")

    return technicians


def read_program_data(file):
    try:
        with open(file, encoding="utf-8") as f:
            program_data_dict = json.load(f)
    except FileNotFoundError:
        raise Exception("Fatal Error! Program Data file not found.")
    return program_data_dict


def store_technicians_data(technicians):
    list_to_store = []
    for technician in technicians:
        list_to_store.append(technician.to_dict())
    with open("technicians_data.json", "w", encoding="utf-8") as f:
        json.dump(list_to_store, f)


def store_program_data(program):
    month = program.month + 1
    year = program.year
    if month == 13:
        year += 1
        month = 1
    next_month_order = []
    for day in range(len(program.guards_program) - program.active_technicians, len(program.guards_program)):
        next_month_order.append(program.guards_program[day].technician_id)
    program_data_dict = {
        "full_program": 0,
        "number_of_technicians": program.number_of_technicians,
        "active_technicians": program.active_technicians,
        "month": month,
        "year": year,
        "sequence": next_month_order,
        "technicians_out_of_order": program.next_month_out_of_order_technicians,
        "empty_slots": [0]
    }
    with open("program_data_test.json", "w", encoding="utf-8") as f:
        json.dump(program_data_dict, f)


def main():
    try:
        technicians_data_file = "technicians_data.json"
        program_data_file = "program_data_test.json"

        technicians = read_technicians_data(technicians_data_file)
        program_data = read_program_data(program_data_file)
        program = Program(program_data, technicians)
        program.initialization()
    except Exception as e:
        print(e)
    else:
        if not program.full_program:
            program.set_empty_days()
        # First place technician to program according who are out of order
        if program.has_technicians_out_of_order():
            for i in range(len(program.technicians_out_of_order)):
                tech_id = program.technicians_out_of_order[i]["technician_id"]
                from_day = program.technicians_out_of_order[i]["from_day"]
                first_guard = program.technicians_out_of_order[i]["first_guard"]
                reason = program.technicians_out_of_order[i]["reason"]

                next_free_day = program.next_available_day(first_guard)
                technician = program.find_technician_by_id(tech_id)
                if technician.is_available(next_free_day):
                    program.guards_program[next_free_day].technician_id = technician.tech_id
                    technician.update_technician_program(reason, 1, next_free_day)
                    technician.update_technician_program("ΥΠ", next_free_day)
                    program.active_technicians += 1
                else:
                    reason, from_day, next_guard = technician.calculate_next_guard(next_free_day)
                    technician.update_technician_program(reason, from_day, next_guard - 1)
                    program.guards_program[next_guard].technician_id = technician.tech_id
        # Place technician to program according to sequence from input file
        for tech in program.sequence:
            next_free_day = program.next_available_day(0)
            technician = program.find_technician_by_id(tech)
            while not technician.is_available(next_free_day):
                # Calculate return day and update technician program
                reason, from_day, next_guard = technician.calculate_next_guard(next_free_day)
                technician.update_technician_program(reason, from_day, next_guard - 1)
                previous_day = next_guard
                while not technician.is_available(next_guard):
                    reason, from_day, next_guard = technician.calculate_next_guard(previous_day)
                    technician.update_technician_program(reason, from_day, next_guard - 1)
                # Place technician to next guard after absence
                if next_guard <= program.days_of_month:
                    program.guards_program[next_guard].technician_id = technician.tech_id
                    technician.update_technician_program("ΥΠ", next_guard)
                else:  # if next guard is in the next month check it
                    program.add_technician_to_next_month(technician.tech_id, next_free_day,
                                                         next_guard - program.days_of_month, reason)
                # Reduce the number of available technicians by one
                program.active_technicians -= 1
                break
            else:
                program.guards_program[next_free_day].technician_id = technician.tech_id
                technician.update_technician_program("ΥΠ", next_free_day)

        # Place techicians the following days until the end of the month
        next_day = program.next_available_day(0)

        for day in range(next_day, program.days_of_month):
            if program.day_is_empty(day):
                technician = program.find_next_technician(day)
                while not technician.is_available(day):
                    # calculate day of return
                    reason, from_day, next_guard = technician.calculate_next_guard(day)
                    technician.update_technician_program(reason, from_day, next_guard)
                    previous_day = next_guard
                    while not technician.is_available(next_guard):
                        reason, from_day, next_guard = technician.calculate_next_guard(previous_day)
                        technician.update_technician_program(reason, from_day, next_guard)
                    # calculate possible day off after the practice
                    if technician.days_at_school:
                        offs = day - technician.days_at_school[0]
                        next_guard += offs
                    # Place technician to the next guard
                    if next_guard < program.days_of_month:
                        program.guards_program[next_guard].technician_id = technician.tech_id
                        technician.update_technician_program("ΥΠ", next_guard)
                    else:  # if next guard is in the next month check it
                        program.add_technician_to_next_month(technician.tech_id, from_day,
                                                             next_guard - program.days_of_month + 1, reason)
                    # Reduce the number of available technicians by one
                    program.active_technicians -= 1
                    # Find the next technician in queue
                    technician = program.find_next_technician(day)
                program.guards_program[day].technician_id = technician.tech_id
                technician.update_technician_program("ΥΠ", day)
            elif program.guards_program[day].technician_id != "/":
                program.active_technicians += 1

        print(program)

        # Εκτύπωση προγράμματος τεχνικών
        # for tech in technicians:
        #     print(f"{tech.surname}")
        #     for day in tech.technician_program:
        #         print(f"{day} ", end="")
        #     print()

        # Creation of program_data.json file
        while True:
            user_choice = input("Θέλεις να αποθηκεύσεις το πρόγραμμα και τα δεδομένα του; (1:Ναι, 2:ΌΧι): ").strip()
            if not user_choice.isdigit():
                print("Δώσε ψηφία παρακαλώ")
                continue
            user_choice = int(user_choice)
            if (user_choice < 0) or (user_choice > 2):
                print("Δώσε έγκυρα ψηφία")
                continue
            if user_choice == 1:
                program.store_program()
                store_program_data(program)
                print("Το πρόγραμμα και τα στοιχεία του προγράμματος αποθηκεύτηκαν με επιτυχία")
            break


main()
