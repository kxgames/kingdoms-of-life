
class ValueTrait:
    """ A single, unconstrained floating number. """

    def __init__(self, value=0):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __call__(self):
        return self.value

class NormalizedTrait(ValueTrait):
    """ A single floating number between 0 and 1, inclusive. """

    def __init__(self, value=0.0):
        ValueTrait.__init__(self, self.clamp_value(value))

    def clamp_value(self, value):
        if value < 0:
            return 0.0
        elif value > 1:
            return 1.0
        else:
            return value

    @value.setter
    def value(self, new_value):
        self._value = self.clamp_value(new_value)

class GaussTrait:
    """ A single Gaussian distribution. """

    def __init__(self, mean=0, stddev=1):
        self._mean = mean
        self._stddev = stddev
    
    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, new_mean):
        self._mean = new_mean

    @property
    def stddev(self):
        return self._stddev

    @stddev.setter
    def stddev(self, new_stddev):
        self._stddev = new_stddev

