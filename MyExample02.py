# -*- coding: utf-8 -*-
from Components import Config
from Components import SquareWaveOscillator
from Components import Clock
from Components import Renderer
from Components import WaveFileSink

from Sequencer import Sequencer
from Sequencer import MMLCompiler

MML1 = "t240o4l4cdefedcrefgagfercrcrcrcrl16crcrdrdrererfrfrl4edcr"
MML2 = "t240o4l4rrrrrrrrcdefedcrefgagfercrcrcrcrl16crcrdrdrererfrfrl4edcr"
MML3 = "t240o4l4rrrrrrrrrrrrrrrrefedcrefgagfercrcrcrcrl16crcrdrdrererfrfrl4edcr"

def main():
    mml_compiler1 = MMLCompiler()
    mml_compiler2 = MMLCompiler()
    mml_compiler3 = MMLCompiler()
    music_sequence1 = mml_compiler1.to_sequence(MML1)
    music_sequence2 = mml_compiler2.to_sequence(MML2)
    music_sequence3 = mml_compiler3.to_sequence(MML3)

    osc1 = SquareWaveOscillator()
    osc2 = SquareWaveOscillator()
    osc3 = SquareWaveOscillator()
    sequencer = Sequencer()
    sequencer.add_track(0, "tone1", osc1, osc1) # 一つ目のoscが周波数をかえる先(オシレーター)、２つ目はデータを取り出す元(通常ならばアンプとかミキサー）
    sequencer.add_track(1, "tone2", osc2, osc2)
    sequencer.add_track(2, "tone3", osc3, osc3)

    sequencer.add_sequence(0, music_sequence1)
    sequencer.add_sequence(1, music_sequence2)
    sequencer.add_sequence(2, music_sequence3)

    sink = WaveFileSink(output_file_name="output.wav")
    clock = Clock()
    renderer = Renderer(clock=clock, source=sequencer, sink=sink)
    renderer.do_rendering()


if __name__ == "__main__":
    main()
