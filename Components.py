# -*- coding: utf-8 -*-
import struct
import wave
import math
import random
import itertools

class Config(object):
    SampleRate = 44100
    SampleWidth = 2
    SampleBits = SampleWidth * 8
    ValueRange = ((2 ** SampleBits / 2 - 1), -(2 ** SampleBits / 2))
    MaxGain = ValueRange[0]
    DataTypeSignature = 'h'
    Channels = 2


class Oscillator(object):
    def __init__(self, frequency=440.0, duty=1.0):
        self.frequency = frequency
        self.duty = duty

    def get_value(self, tick):
        raise NotImplemented()


class ConstantValueGenerator(object):
    def __init__(self, value=0):
        self.value = value


    def get_value(self, tick):
        return [self.value,] * Config.Channels



class NoiseGenerator(Oscillator):
    def __init__(self, frequency=44100):
        super(self.__class__, self).__init__(frequency=frequency)
        self.current_value = random.uniform(-1.0, 1.0)

    def get_value(self, tick):
        if (tick % (Config.SampleRate / self.frequency)) == 0:
            self.current_value = random.uniform(-1.0, 1.0)

        return [self.current_value,] * Config.Channels



class SineWaveOscillator(Oscillator):
    def get_value(self, tick):
        value = math.sin((2.0 * math.pi) * \
                         (self.frequency / Config.SampleRate) * \
                         tick + (64 / math.pi))

        return [value,] * Config.Channels



class SquareWaveOscillator(Oscillator):
    def __init__(self, frequency=440.0, duty=0.5):
        super(self.__class__, self).__init__(frequency=frequency, duty=duty)
        self.current_value = 1

    def get_value(self, tick):
        l = Config.SampleRate / self.frequency
        change_point = l * self.duty

        if (tick % l) <= change_point:
            return [1,] * Config.Channels
        else:
            return [-1,] * Config.Channels



class SawWaveOscillator(Oscillator):
    def get_value(self, tick):
        l = Config.SampleRate / self.frequency
        value = -2 * (tick % l) / (l / (1.0 / self.duty)) + 1
        if value < -1:
            value = -1
        return [value,] * Config.Channels



class LFO(object):
    def __init__(self, oscillator_class=None, frequency=2, duty=1.0):
        self.oscillator = oscillator_class(frequency=frequency, duty=duty)


    def get_value(self, tick):
        value = (self.oscillator.get_value(tick)[0] + 1) / 2.0
        return value



class Amplifeir(object):
    def __init__(self, source=None, gain=0, attenuate=1.0):
        self.source = source
        self.gain = gain
        self.attenuate = attenuate


    def get_value(self, tick):
        gained_values = list()
        for value in self.source.get_value(tick):
            value *= self.gain
            value = min((Config.ValueRange[0], value))
            value = max((Config.ValueRange[1], value))
            gained_values.append(value)

        return [value * self.attenuate for value in gained_values]


class Compressor(object):
    def __init__(self, source=None, threshold=1.0, ratio=1.0):
        self.source = source
        self.threshold = threshold
        self.ratio = ratio


    def get_value(self, tick):
        result = list()
        for value in self.soruce.get_value(tick):
            if value >= self.threshold:
                pass


class Clock(object):
    def __init__(self, end=None):
        self.tick = -1
        self.end = end


    def next(self):
        self.tick += 1
        if (self.end is not None) and (self.tick > self.end):
            return None
        else:
            return self.tick


class Multiplication(object):
    def __init__(self, multiplicand, multiplicator):
        self.multiplicand = multiplicand
        self.multiplicator = multiplicator


    def get_value(self, tick):
        multiplicand_value = self.multiplicand.get_value(tick)
        multiplicator_value = self.multiplicator.get_value(tick)

        return [value * multiplicator_value for value in multiplicand_value]


class Subtraction(object):
    def __init__(self, minuend, subtrahend):
        self.minuend = minuend
        self.subtrahend = subtrahend


    def get_value(self, tick):
        return [(x - y) for (x, y) in zip(self.minuend.get_value(tick), self.subtrahend.get_value(tick))]


class Inverter(object):
    def __init__(self, source=None):
        self.source = source


    def get_value(self, tick):
        return [-value for value in self.source.get_value(tick)]



class Gate(object):
    def __init__(self, source=None, state=list()):
        self.source = source
        self.state = state

    def get_value(self, tick):
        return [(value if state is True else 0) for (state, value) in zip(self.state, self.source.get_value(tick))]



class FrequencyModulator(object):
    def __init__(self, source=None, delta=None):
        self.source = source
        self.delta = delta


    def get_value(self, tick):
        detuning = self.delta.get_value(tick)[0]
        self.source.frequency += detuning
        result = self.source.get_value(tick)
        self.source.frequency -= detuning
        return result



class Mixer(object):
    def __init__(self):
        self.tracks = dict()


    def add_track(self, track_id, track_name, track_source):
        self.tracks[track_id] = (track_name, track_source)


    def get_value(self, tick):
        result = [0.0,] * Config.Channels
        for (track_id, (name, source)) in self.tracks.iteritems():
            result = [sum(x) for x in zip(result, source.get_value(tick))]

        return [value / len(self.tracks) for value in result]


class Renderer(object):
    def __init__(self, clock=None, source=None, sink=None):
        self.clock = clock
        self.source = source
        self.sink = sink


    def do_rendering(self):
        self.sink.open()

        while True:
            tick = self.clock.next()
            if tick is None:
                break

            data = self.source.get_value(tick)
            if data is None:
                break

            self.sink.write(data)

            if (tick % 50000) == 0:
                print("%10d ... " % tick)

        self.sink.close()



class WaveFileSink(object):
    def __init__(self, output_file_name="output.wav"):
        self.output_file_name = output_file_name


    def open(self):
        self.output_wave_file = wave.open(self.output_file_name, "wb")
        self.output_wave_file.setnchannels(Config.Channels)
        self.output_wave_file.setsampwidth(Config.SampleWidth)
        self.output_wave_file.setframerate(Config.SampleRate)


    def close(self):
        self.output_wave_file.close()


    def write(self, data):
        self.output_wave_file.writeframesraw("".join(
            [struct.pack(Config.DataTypeSignature, x) for x in data]))
