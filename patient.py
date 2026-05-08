from datetime import datetime

class Patient:
    def __init__(self, name, pain_level):
        # store patient name
        self.name = name

        # store pain level
        self.pain_level = pain_level

        # save current check-in time
        self.check_in_time = datetime.now()

    def wait_time_minutes(self):
        # calculate time difference since check-in
        delta = datetime.now() - self.check_in_time

        # convert seconds into minutes
        return round(delta.total_seconds() / 60, 1)

    def __repr__(self):
        # return formatted patient information
        return (f"{self.name} | Pain: {self.pain_level} | "
                f"Checked in: {self.check_in_time.strftime('%H:%M:%S')} | "
                f"Waited: {self.wait_time_minutes()} min")