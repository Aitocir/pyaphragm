import json
import sys
import time
import array
import math
import simpleaudio as sa

from band import Instrument

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

print(time.time()-start)

a = sa.WaveObject(sound, 1, 2, 44100)
b = a.play()
b.wait_done()