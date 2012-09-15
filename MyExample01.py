# -*- coding: utf-8 -*-
from Components import Config
from Components import SineWaveOscillator
from Components import MySineWaveOscillator
from Components import SawWaveOscillator
from Components import Amplifeir
from Components import Clock
from Components import Renderer
from Components import WaveFileSink


def main():
    osc = MySineWaveOscillator(frequency=220.0)
    amp = Amplifeir(source=osc, gain=Config.MaxGain, attenuate=0.5)
    sink = WaveFileSink(output_file_name="output.wav")

    output_seconds = 2;
    clock = Clock(end=Config.SampleRate * output_seconds)

    renderer = Renderer(clock=clock, source=amp, sink=sink)
    renderer.do_rendering()


if __name__ == "__main__":
    main()
