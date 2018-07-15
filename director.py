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

#
#  Band setup 
#

with open(sys.argv[1]) as f:
    instrument_defs = json.loads(f.read())

instruments = {}
for thing in instrument_defs:
    instrument = Instrument(thing)
    instruments[instrument.name()] = instrument

#
#  Music reading
#


start = time.time()

"""
sound = array.array('h')
for step in range(6):
    note = instruments['whistle'].play_note(587.33*(2**(step/12)), 44100)
    for n in note:
        sound.append(int(n))
"""


note_C = 440 * (2**(3/12))
note_D = 440 * (2**(5/12))
note_E = 440 * (2**(7/12))
note_G = 440 * (2**(10/12))

music = []
music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))
music.extend(instruments['whistle'].play_note(note_C, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))

music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_E, 44100))

music.extend(instruments['whistle'].play_note(note_D, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))
music.extend(instruments['whistle'].play_note(note_D, 44100))

music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_G, 22050))
music.extend(instruments['whistle'].play_note(note_G, 44100))

music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))
music.extend(instruments['whistle'].play_note(note_C, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))

music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_E, 22050))

music.extend(instruments['whistle'].play_note(note_D, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))
music.extend(instruments['whistle'].play_note(note_E, 22050))
music.extend(instruments['whistle'].play_note(note_D, 22050))

music.extend(instruments['whistle'].play_note(note_C, 88200))

sound = array.array('h')
sound.extend([int(x) for x in music])

sound1 = array.array('h')
reader = MusicReader()
instructions = reader.parse_music('E5Q D5Q C5Q D5Q   E5Q E5Q E5H   D5Q D5Q D5H   E5Q G5Q G5H   E5Q D5Q C5Q D5Q   E5Q E5Q E5Q E5Q   D5Q D5Q E5Q D5Q   C5W')
BPM = 120
FPS = 44100
for cmd in instructions:
    #  TODO: handle more than notes
    sound1.extend([int(x) for x in instruments['whistle'].play_note(cmd['frequency'], (60/BPM)*FPS*(cmd['beats']))])

print(time.time()-start)

a = sa.WaveObject(sound, 1, 2, FPS)
b = a.play()
b.wait_done()

a = sa.WaveObject(sound1, 1, 2, FPS)
b = a.play()
b.wait_done()