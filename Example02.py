# -*- coding: utf-8 -*-
from Components import Config
from Components import SquareWaveOscillator
from Components import Clock
from Components import Renderer
from Components import WaveFileSink

from Sequencer import Sequencer
from Sequencer import MMLCompiler

MML = "t120o4l4cdefedcrefgagfercrcrcrcrl16crcrdrdrererfrfrl4edcr"

def main():
    mml_compiler = MMLCompiler()
    music_sequence = mml_compiler.to_sequence(MML)
    
    osc = SquareWaveOscillator()
    sequencer = Sequencer()
    sequencer.add_track(0, "tone1", osc, osc)
    sequencer.add_sequence(0, music_sequence)

    sink = WaveFileSink(output_file_name="output.wav")
    clock = Clock()
    renderer = Renderer(clock=clock, source=sequencer, sink=sink)
    renderer.do_rendering()


if __name__ == "__main__":
    main()
