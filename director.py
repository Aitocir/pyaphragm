import json
import sys
import time
import array
import math
import simpleaudio as sa

from band import Instrument

class MusicReader:
    def __init__(self):
        self._notenames = 'CdDeEFgGaAbB'
        self._undotted = 'DWHQESTF'
        self._dotted = 'DWHQESTF'.lower()
        self._thirds = '36248'
        self._dynamics = ['ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff']
    def _freq_for_note(self, letter, index):
        nidx = ((int(index)*12)+12) + self._notenames.index(letter)
        return 440 * (2 ** ((nidx-69)/12))
    def _beats_for_length(self, length):
        if length in self._undotted:
            return 8 / (2 ** self._undotted.index(length))
        if length in self._dotted:
            return 12 / (2 ** self._dotted.index(length))
        if length in self._thirds:
            return (4 / (2 ** self._thirds.index(length))) / 3
        #  if we get there, the length wasn't a valid length character
        return 0
    def parse_music(self, sheetmusic):
        #  ignore whitespace so writers can format prettily
        for c in ' \n':
            sheetmusic = sheetmusic.replace(c, '')
        signals = []
        #  TODO: parse more than notes
        notes = [sheetmusic[x:x+3] for x in range(0,len(sheetmusic),3)]
        for note in notes:
            signal = {'type': 'note'}
            signal['beats'] = self._beats_for_length(note[2])
            signal['frequency'] = self._freq_for_note(note[0], note[1])
            signals.append(signal)
        return signals
    def read_dynamic(self, dynamic):
        if dynamic not in self._dynamics:
            return 0
        return (self._dynamics.index(dynamic) + 1) / 8

#
#  Band setup 
#

with open(sys.argv[1]) as f:
    instrument_defs = json.loads(f.read())

instruments = {}
for thing in instrument_defs:
    instrument = Instrument(thing)
    instruments[instrument.name()] = instrument

with open(sys.argv[2]) as f:
    composition = json.loads(f.read())

#
#  Music reading
#


start = time.time()

sound1 = array.array('h')
reader = MusicReader()
BPM = composition['bpm']
FPS = 44100
volume = reader.read_dynamic(composition['dynamic'])
musics = []
for part in composition['parts']:
    instrument_name = composition['parts'][part]
    instructions = reader.parse_music(composition['score'][part])
    musics.append([])
    count = 0
    for cmd in instructions:
        #  TODO: handle more than notes
        musics[-1].extend(instruments[instrument_name].play_note(cmd['frequency'], (60/BPM)*FPS*cmd['beats']))
        count += 1
        instruments[instrument_name].set_legato(count > 12)

score_len = min([len(x) for x in musics])
for i in range(score_len):
    sound1.append(int(sum([x[i] for x in musics]) / len(musics)))

print(time.time()-start)

a = sa.WaveObject(sound1, 1, 2, FPS)
b = a.play()
b.wait_done()