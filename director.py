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
sound = array.array('h')
for step in range(6):
    note = instruments['whistle'].play_note(587.33*(2**(step/12)), 44100)
    for n in note:
        sound.append(int(n))
print(time.time()-start)

a = sa.WaveObject(sound, 1, 2, 44100)
b = a.play()
b.wait_done()