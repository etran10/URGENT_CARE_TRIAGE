import os
from patient import Patient
from triage_queue import TriageQueue
from queries import who_waited_over, still_at_pain_level
from providers import Provider, ProviderPool

# ── helpers ───────────────────────────────────────────────
def clear():
    os.system('clear')

def pause(msg="  Press Enter to continue..."):
    input(f"\n{msg}")

# ── setup ─────────────────────────────────────────────────
queue = TriageQueue()
pool  = ProviderPool()

pool.add_provider(Provider("Dr. Smith",   "MD"))
pool.add_provider(Provider("Nurse Kelly", "NP"))
pool.add_provider(Provider("Dr. Patel",   "PA"))

# ── auto-assign logic ─────────────────────────────────────
def try_auto_assign():
    available = pool.get_available()
    next_patient = queue.call_next()
    if available and next_patient:
        provider = pool.assign_next(next_patient)
        return next_patient, provider
    elif next_patient:
        queue.add_patient(next_patient)
    return None, None

# ── queue position ────────────────────────────────────────
def show_queue_position(patient):
    clear()
    print("─" * 40)
    print("   YOUR PLACE IN LINE")
    print("─" * 40)
    print()

    all_waiting = sorted(
        queue.all_patients(),
        key=lambda x: (-x.pain_level, x.check_in_time)
    )

    position = next(
        (i + 1 for i, p in enumerate(all_waiting)
         if p.name.lower() == patient.name.lower()), None
    )

    if position is None:
        print("  You are not currently in the queue.")
        print("  You may have already been assigned")
        print("  to a provider.")
        print()
        pause()
        return

    print(f"  You are number {position} in line.")
    print()

    ahead = [p for p in all_waiting
             if p.name.lower() != patient.name.lower()][:position - 1]

    if not ahead:
        print("  Nobody is ahead of you —")
        print("  you are next to be seen!")
    else:
        print("  Patient(s) ahead of you:")
        print()
        for i, p in enumerate(ahead):
            print(f"    {i + 1}. {p.name} — Pain level {p.pain_level} "
                  f"| Waited {p.wait_time_minutes()} min")

    print()
    print("─" * 40)
    pause("  Press Enter to return to the main menu...")

# ── check-in flow ─────────────────────────────────────────
def checkin_flow():
    clear()
    print("─" * 40)
    print("   NEW PATIENT CHECK-IN")
    print("─" * 40)
    print()

    name = input("  What is your name? ").strip()
    if not name:
        print("  Name cannot be blank.")
        pause()
        return

    clear()
    print("─" * 40)
    print(f"   Hi, {name}!")
    print("─" * 40)
    print()
    print("  On a scale of 1 to 5, what is your")
    print("  current pain level?")
    print()
    print("    1 — Minimal / Not urgent")
    print("    2 — Mild")
    print("    3 — Moderate")
    print("    4 — Severe")
    print("    5 — Most urgent")
    print()

    while True:
        try:
            level = int(input("  Enter a number (1-5): "))
            if 1 <= level <= 5:
                break
            else:
                print("  Please enter a number between 1 and 5.")
        except ValueError:
            print("  Please enter a number between 1 and 5.")

    p = Patient(name, level)
    queue.add_patient(p)
    patient, provider = try_auto_assign()

    clear()
    print("─" * 40)
    if patient and provider:
        print("   A PROVIDER IS READY FOR YOU!")
        print("─" * 40)
        print()
        print(f"  Name:       {name}")
        print(f"  Pain level: {level}")
        print()
        print(f"  Please proceed to see {provider.name}.")
        print()
        print("─" * 40)
        pause()
    else:
        print("   YOU'RE CHECKED IN!")
        print("─" * 40)
        print()
        print(f"  Name:       {name}")
        print(f"  Pain level: {level}")
        print()
        print("  Please have a seat.")
        print("  A provider will be with you shortly.")
        print()
        print("─" * 40)
        print()
        see_line = input("  Would you like to see your place in line? (yes/no): ").strip().lower()
        if see_line in ("yes", "y"):
            show_queue_position(p)
        else:
            pause()

# ── update status flow ────────────────────────────────────
def update_status_flow():
    clear()
    print("─" * 40)
    print("   UPDATE YOUR STATUS")
    print("─" * 40)
    print()

    name = input("  What is your name? ").strip()
    patients = queue.all_patients()
    match = next((p for p in patients if p.name.lower() == name.lower()), None)

    if not match:
        clear()
        print("─" * 40)
        print("   NAME NOT FOUND")
        print("─" * 40)
        print()
        print(f"  We couldn't find '{name}' in the system.")
        print("  Please check in at the front desk.")
        print()
        pause()
        return

    # Question 1 — Wait time
    clear()
    print("─" * 40)
    print(f"   Hi again, {match.name}!")
    print("─" * 40)
    print()
    print("  How long have you been waiting?")
    print()
    print("  1. Less than 30 minutes")
    print("  2. 30 – 60 minutes")
    print("  3. 1 – 2 hours")
    print("  4. More than 2 hours")
    print()

    wait_choice = input("  Enter a number (1-4): ").strip()
    wait_labels = {
        "1": "Less than 30 minutes",
        "2": "30 – 60 minutes",
        "3": "1 – 2 hours",
        "4": "More than 2 hours"
    }
    wait_response = wait_labels.get(wait_choice, "Unknown")

    # Question 2 — Pain change
    clear()
    print("─" * 40)
    print("   ONE MORE QUESTION")
    print("─" * 40)
    print()
    print("  Has your pain level changed")
    print("  since you first checked in?")
    print()
    print(f"  Your current level on file: {match.pain_level}")
    print()
    print("  1. Yes, it is worse")
    print("  2. Yes, it has improved")
    print("  3. No, it is the same")
    print()

    pain_choice = input("  Enter a number (1-3): ").strip()

    if pain_choice == "1":
        print()
        print("  On a scale of 1–5, what is your")
        print("  new pain level?")
        print()
        while True:
            try:
                new_level = int(input("  Enter a number (1-5): "))
                if 1 <= new_level <= 5:
                    break
                else:
                    print("  Please enter a number between 1 and 5.")
            except ValueError:
                print("  Please enter a number between 1 and 5.")
        match.pain_level = new_level
        pain_response = f"Updated to level {new_level}"
        patient, provider = try_auto_assign()
    elif pain_choice == "2":
        pain_response = "Improved — level unchanged in system"
        patient, provider = None, None
    else:
        pain_response = "No change"
        patient, provider = None, None

    # Summary
    clear()
    print("─" * 40)
    if patient and provider:
        print("   A PROVIDER IS READY FOR YOU!")
    else:
        print("   STATUS UPDATED")
    print("─" * 40)
    print()
    print(f"  Name:         {match.name}")
    print(f"  Wait time:    {wait_response}")
    print(f"  Pain status:  {pain_response}")
    print()
    if patient and provider:
        print(f"  Please proceed to see {provider.name}.")
        print()
        print("─" * 40)
        pause()
    else:
        print("  Thank you! Please return to your seat.")
        print("  A provider will be with you shortly.")
        print()
        print("─" * 40)
        print()
        see_line = input("  Would you like to see your place in line? (yes/no): ").strip().lower()
        if see_line in ("yes", "y"):
            show_queue_position(match)
        else:
            pause()

# ── staff dashboard ───────────────────────────────────────
def staff_menu():
    STAFF_PASSWORD = "admin123"
    clear()
    pwd = input("  Enter staff password: ").strip()
    if pwd != STAFF_PASSWORD:
        clear()
        print("  Incorrect password.")
        pause()
        return

    while True:
        clear()
        print("─" * 40)
        print("   STAFF DASHBOARD")
        print("─" * 40)
        print()
        print("  1. View all waiting patients")
        print("  2. Call next patient")
        print("  3. Who waited over X minutes?")
        print("  4. Who is at pain level X?")
        print("  5. View provider availability")
        print("  6. Mark provider as available")
        print("  7. Back to kiosk")
        print()
        print("─" * 40)

        choice = input("  Enter choice: ").strip()

        if choice == "1":
            clear()
            patients = queue.all_patients()
            print("─" * 40)
            print("  WAITING PATIENTS")
            print("─" * 40)
            if patients:
                for p in sorted(patients, key=lambda x: -x.pain_level):
                    print(f"  {p}")
            else:
                print("  No patients waiting.")
            pause()

        elif choice == "2":
            clear()
            available = pool.get_available()
            if not available:
                print("  ⚠ No providers available.")
            else:
                p = queue.call_next()
                if not p:
                    print("  Queue is empty.")
                else:
                    provider = pool.assign_next(p)
                    print(f"  → {p.name} (level {p.pain_level}) assigned to {provider.name}.")
            pause()

        elif choice == "3":
            clear()
            mins = float(input("  Minutes threshold: "))
            results = who_waited_over(queue.all_patients(), mins)
            print(f"\n  {len(results)} patient(s) waiting over {mins} min:")
            for p in results:
                print(f"  {p}")
            pause()

        elif choice == "4":
            clear()
            level = int(input("  Pain level to search: "))
            results = still_at_pain_level(queue.all_patients(), level)
            print(f"\n  {len(results)} patient(s) at pain level {level}:")
            for p in results:
                print(f"  {p}")
            pause()

        elif choice == "5":
            clear()
            print("─" * 40)
            print("  PROVIDER STATUS")
            print("─" * 40)
            for prov in pool.get_all():
                print(f"  {prov}")
            print(f"\n  {len(pool.get_available())} of {len(pool.get_all())} available.")
            pause()

        elif choice == "6":
            clear()
            providers = pool.get_all()
            for i, prov in enumerate(providers):
                print(f"  {i+1}. {prov}")
            idx = int(input("\n  Enter number to mark as available: ")) - 1
            if 0 <= idx < len(providers):
                providers[idx].free_up()
                print(f"  ✓ {providers[idx].name} is now available.")
            pause()

        elif choice == "7":
            break

# ── welcome screen ────────────────────────────────────────
def welcome_screen():
    clear()
    print("─" * 40)
    print("   WELCOME TO URGENT CARE")
    print("   Patient Check-In Kiosk")
    print("─" * 40)
    print()
    print("  Please select an option:")
    print()
    print("  1. Check In")
    print("  2. Update My Status")
    print()
    print("─" * 40)

# ── main loop ─────────────────────────────────────────────
while True:
    welcome_screen()
    choice = input("  Enter choice: ").strip().lower()

    if choice == "1":
        checkin_flow()
    elif choice == "2":
        update_status_flow()
    elif choice == "staff":
        staff_menu()
    else:
        clear()
        print("  Invalid choice. Please try again.")
        pause()