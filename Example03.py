class Vibrato(object):
    def __init__(self, source=None, frequency=1.0, depth=1.0):
        viv_oscillator = SineWaveOscillator(frequency=frequency)
        amp = Amplifeir(source=viv_oscillator, gain=depth, attenuate=1.0)
        self.output = FrequencyModulator(source=source, diff=amp)

    def get_value(self, tick):
        return self.output.get_value(tick)



class DeTunedSquareWaveOscillator(object):
    def __init__(self, frequency=0, depth=0):
        self.depth = depth
        self.osc1 = SquareWaveOscillator(frequency=frequency)
        self.osc2 = SquareWaveOscillator(frequency=frequency + depth)

        self.mixer = Mixer()
        self.mixer.add_track(0, "base_tone", self.osc1)
        self.mixer.add_track(1, "detuned_tone", self.osc2)


    def get_value(self, tick):
        return self.mixer.get_value(tick)


    def get_frequency(self):
        return self.osc1.frequency


    def set_frequency(self, value):
        self.osc1.frequency = value
        self.osc2.frequency = value + self.depth

    frequency = property(get_frequency, set_frequency)

