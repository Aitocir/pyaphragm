import json
import sys

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



sound = array.array('h')
note = instrument.play_note(440, 88200)
for n in note:
    sound.append(int(n))

a = sa.WaveObject(sound, 1, 2, 44100)
b = a.play()
b.wait_done()