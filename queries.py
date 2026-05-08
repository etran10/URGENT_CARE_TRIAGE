def who_waited_over(patients, minutes):
    results = [p for p in patients if p.wait_time_minutes() >= minutes]
    return sorted(results, key=lambda p: p.wait_time_minutes(), reverse=True)

def still_at_pain_level(patients, level):
    return [p for p in patients if p.pain_level == level]