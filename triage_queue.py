import heapq

class TriageQueue:
    def __init__(self):
        # store patients in a priority heap
        self._heap = []

        # keeps track of order patients were added
        self._counter = 0

    def add_patient(self, patient):
        # add patient based on pain level priority
        heapq.heappush(self._heap, (-patient.pain_level, self._counter, patient))

        # increase counter after adding patient
        self._counter += 1

    def call_next(self):
        # check if there are patients in the queue
        if self._heap:

            # remove highest priority patient
            _, _, patient = heapq.heappop(self._heap)

            # return the patient object
            return patient

        # return None if queue is empty
        return None

    def all_patients(self):
        # return a list of all patients in the heap
        return [p for (_, _, p) in self._heap]