# -*- coding: utf-8 -*-
import pprint
from Components import Config
from Components import Clock
from Components import ConstantValueGenerator
from Components import NoiseGenerator
from Components import SineWaveOscillator
from Components import SquareWaveOscillator
from Components import SawWaveOscillator
from Components import LFO
from Components import Multiplication
from Components import Subtraction
from Components import Inverter
from Components import Gate
from Components import FrequencyModulator
from Components import Mixer
from Components import Amplifire
from Components import Renderer
from Components import WaveFileSink

from Sequencer import MMLCompiler
from Sequencer import Sequencer

def percusstion_test():
    bass_base = Subtraction(SineWaveOscillator(frequency=40.0),
                            Amplifire(source=SquareWaveOscillator(frequency=80.0, duty=0.125),
                                      gain=1,
                                      attenuate=0.075))

    bass_drum = Multiplication(bass_base,
                               LFO(oscillator_class=SawWaveOscillator, frequency=1.0, duty=0.5))

    snare_drum = Multiplication(NoiseGenerator(frequency=6000.0),
                                LFO(oscillator_class=SawWaveOscillator, frequency=1.0, duty=0.25))
    
    hihat = Multiplication(NoiseGenerator(frequency=44100.0),
                           LFO(oscillator_class=SawWaveOscillator, frequency=4.0, duty=0.25))


    mixer = Mixer()
    mixer.add_track(0, "bus_drum", bass_drum)
    mixer.add_track(1, "snare_drum", snare_drum)
    mixer.add_track(2, "hihat", hihat)
    
    amplifire = Amplifire(source=mixer, gain=Config.ValueRange[0], attenuate=1.0)
    sink = WaveFileSink(output_file_name="output.wav")
    clock = Clock(end=Config.SampleRate * 3)

    renderer = Renderer(clock=clock, source=amplifire, sink=sink)
    renderer.do_rendering()


def chorus_test():
    osc1 = SquareWaveOscillator(frequency=440.0)
    osc2 = Inverter(source=FrequencyModulator(source=osc1,
                                              delta=Multiplication(
                                                  ConstantValueGenerator(2.0),
                                                  LFO(oscillator_class=SineWaveOscillator,
                                                      frequency=3.0))))
        

    mixer = Mixer()
    mixer.add_track(0, "base_tone", Gate(source=osc1, state=(True, False)))
    mixer.add_track(1, "detuned_tone", Gate(source=osc2, state=(True, True)))

    amplifire = Amplifire(source=mixer, gain=Config.MaxGain, attenuate=0.75)
    sink = WaveFileSink(output_file_name="output.wav")
    clock = Clock(end=Config.SampleRate)

    renderer = Renderer(clock=clock, source=amplifire, sink=sink)
    renderer.do_rendering()


class Tone(object):
    def __setattr__(self, name, value):
        if name == "frequency":
            self.osc1.frequency = value
            self.osc2.frequency = value
        else:
            object.__setattr__(self, name, value)
                
    
    def __init__(self):
        self.osc1 = SquareWaveOscillator()
        self.osc2 = SquareWaveOscillator()
        
        mod_osc2 = Inverter(source=FrequencyModulator(source=self.osc2,
                                                  delta=ConstantValueGenerator(2.0)))

        self.mixer = Mixer()
        self.mixer.add_track(0, "base_tone", Gate(source=self.osc1, state=(True, False)))
        self.mixer.add_track(1, "detuned_tone", Gate(source=mod_osc2, state=(False, True)))


    def get_value(self, tick):
        return self.mixer.get_value(tick)
        
        


def compiler_test():
    mmls = ("t115o5l8f2r8cfa>c<ar8fgr8ggr8d4r8gfr8ef2r8cfa>c<ar8fg-r8g-g-r8f1r8",
            "t115o4l8a2r8aa>cfcr8<ab-r8b-b-r8b-4r8b-b-r8b-a2r8aa>cfcr8<ab-r8b-b-r8a1r8",
            "t115o2l16v6f.r32f.r32f.r32f.r32r4f.r32f.r32f.r32f.r32r4"
            "f.r32f.r32f.r32f.r32r4f.r32f.r32f.r32f.r32r4"
            "f.r32f.r32f.r32f.r32r4f.r32f.r32f.r32f.r32r4"
            "f.r32f.r32f.r32f.r32r8f1r8")
    
    
    mml_compiler = MMLCompiler()
    sequences = [mml_compiler.to_sequence(mml) for mml in mmls]
    tones = [Tone(), Tone(), SquareWaveOscillator()]
                    
    seq = Sequencer()
    seq.add_track(0, "track_0", tones[0], tones[0])
    seq.add_track(1, "track_1", tones[1], tones[1])
    seq.add_track(2, "track_3", tones[2], tones[2])
    
    seq.add_sequence(0, sequences[0])
    seq.add_sequence(1, sequences[1])
    seq.add_sequence(2, sequences[2])
    
    sink = WaveFileSink(output_file_name="output.wav")
    clock = Clock()

    renderer = Renderer(clock=clock, source=seq, sink=sink)
    renderer.do_rendering()

        

def main():
    # percusstion_test()
    compiler_test()
    

if __name__ == "__main__":
    main()
