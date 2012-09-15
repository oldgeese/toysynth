# -*- coding: utf-8 -*-
import re
import math
from Components import Config
from Components import Clock
from Components import Mixer
from Components import Amplifier


class MMLCompiler(object):
    def __init__(self, tuning=440, tempo=120, octave=4, on_length=4, volume=8):
        self.tick_position = 0
        self.tuning = tuning
        self.tempo = tempo
        self.octave = octave
        self.on_length = on_length
        self.volume = volume

        self.note_diff = {"c":  -9, "c+": -8, "d-": -8, "d":  -7, "d+": -6,
                          "e-": -6, "e":  -5, "f":  -4, "f+": -3, "g-": -3,
                          "g":  -2, "g+": -1, "a-": -1, "a":   0, "a+":  1,
                          "b-": 1, "b": 2, "r": None}

        self.note_pattern = re.compile(r"^([a-g]|r)(\+|\#|\-)?(\d+)?(\.)?", re.IGNORECASE)
        self.command_pattern = re.compile(r"^(t|l|v|o)(\d+)(\.)?", re.IGNORECASE)
        self.octave_up_down_pattern = re.compile(r"(\<|\>)")


    def to_sequence(self, mml):
        mml = mml.lower()
        sequence = list()
        read_position = 0

        while read_position < len(mml):
            note_match = self.note_pattern.search(mml[read_position:])
            if note_match:
                # 音符の処理
                (note_code, accidential, on_length, period) = note_match.groups()

                # 発声長の取得
                note_length = int(on_length) if on_length else self.on_length
                note_on_tick = (Config.SampleRate / 1.0) * (60.0 / self.tempo) * (4.0 / note_length)

                # 符点があったら音長を1.5倍にする
                note_on_tick *= 1.5 if period else 1.0

                # 発声終了時刻を更新する
                self.tick_position += note_on_tick

                # 音程の取得と周波数の計算
                if note_code == "r":
                    cut_off = True
                    note_frequency = 1

                else:
                    cut_off = False
                    note_diff = self.note_diff[note_code]

                    # 半音符号の処理
                    if accidential:
                        if accidential in "#+":
                            note_diff += 1
                        elif accidential == "-":
                            note_diff -= 1

                    # 周波数の取得(平均12律)
                    note_frequency = self.tuning * \
                                     (2 ** (self.octave - 4)) * \
                                     ((2 ** note_diff) ** (1 / 12.0))


                # 音量指示をアッテネーター値に計算
                attenuate = 0.0 if cut_off else (self.volume / 15.0)

                # シーケンスに記録
                sequence.append((attenuate, note_frequency, int(self.tick_position)))
                read_position += note_match.end()
                continue


            # コマンド系文字の処理
            command_match = self.command_pattern.search(mml[read_position:])
            if command_match:
                (command_letter, value, period) = command_match.groups()

                if command_letter == "t":
                    # テンポ
                    self.tempo = int(value)

                elif command_letter == "v":
                    # ボリューム
                    self.volume = int(value)

                elif command_letter == "l":
                    # 既定音長
                    self.on_length = int(value)
                    if period:
                        self.on_length *= 1.5

                elif command_letter == "o":
                    # オクターブ(絶対指定)
                    self.octave = int(value)

                read_position += command_match.end()
                continue

            if mml[read_position] in "<>":
                # オクターブの相対指定
                if mml[read_position] == ">":
                    self.octave += 1
                else:
                    self.octave -= 1

                read_position += 1
                continue

            raise ValueError(
                "Invalid MML syntax at %d on '%s'" % (read_position, mml[read_position:]))

        return sequence


class Sequencer(object):
    def __init__(self):
        self.tracks = dict()
        self.sequences = dict()
        self.mixer = Mixer()


    def add_track(self, track_id, track_name, input_component, output_component):
        output_component = Amplifier(source=output_component,
                                     gain=Config.MaxGain,
                                     attenuate=0.5)
        self.tracks[track_id] = (track_name, input_component, output_component)
        self.mixer.add_track(track_id, track_name, output_component)
        self.sequences[track_id] = list()


    def add_sequence(self, track_id, sequence_data):
        self.sequences[track_id].extend(sequence_data)


    def get_value(self, tick):
        for (track_id, sequence_data) in self.sequences.items():
            if tick > sequence_data[0][2]:
                del sequence_data[0]

            if len(sequence_data) == 0:
                return None

            (attenuate, frequency, off_tick) = sequence_data[0]
            (track_name, input_component, output_component) = self.tracks[track_id]

            input_component.frequency = frequency
            output_component.attenuate = attenuate

        return self.mixer.get_value(tick)




