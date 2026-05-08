class Provider:
    def __init__(self, name, role="Provider"):
        # store provider name
        self.name = name

        # store provider role
        self.role = role

        # provider starts as available
        self.available = True

        # no patient assigned at first
        self.current_patient = None

    def assign_patient(self, patient):
        # mark provider as busy
        self.available = False

        # assign patient to provider
        self.current_patient = patient

    def free_up(self):
        # mark provider as available again
        self.available = True

        # remove current patient
        self.current_patient = None

    def __repr__(self):
        # show provider info if available
        if self.available:
            return f"✓ {self.name} ({self.role}) — Available"
        else:
            # show provider info with patient name
            return f"✗ {self.name} ({self.role}) — With: {self.current_patient.name}"


class ProviderPool:
    def __init__(self):
        # list to store providers
        self._providers = []

    def add_provider(self, provider):
        # add provider to the list
        self._providers.append(provider)

    def get_available(self):
        # return only available providers
        return [p for p in self._providers if p.available]

    def get_all(self):
        # return all providers
        return self._providers

    def assign_next(self, patient):
        # get list of available providers
        available = self.get_available()

        # check if any provider is available
        if available:
            # pick the first available provider
            provider = available[0]

            # assign patient to provider
            provider.assign_patient(patient)

            # return assigned provider
            return provider

        # return None if no providers are available
        return None