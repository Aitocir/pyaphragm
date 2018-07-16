import math

class Instrument:
    def __init__(self, definition):
        self._fps = 44100
        self._volume = 1.0
        self._name = definition['name']
        self._wf = {'sine': self._sine, 'square': self._square, 'triangle': self._tri, 'sawtooth': self._saw}
        self._vibrato = {"cents": 0, "frequency": 0} if 'vibrato' not in definition else definition['vibrato']
        self._tremolo = {"drop": 0, "frequency": 0} if 'tremolo' not in definition else definition['tremolo']
        self._legato = False
        if 'decay' not in definition:
            self._decaytime = 1.0
            self._decayrate = 0.0
            self._decaytype = 'exponential'
        else:
            self._decaytime = definition['decay']['period'] if 'period' in definition['decay'] else 1.0
            self._decayrate = definition['decay']['rate'] if 'rate' in definition['decay'] else 0.0
            self._decaytype = definition['decay']['type'] if 'type' in definition['decay'] else 'exponential'
        if 'buildup' not in definition:
            self._introlen = 0.0
            self._introcurve = 1.0
            self._introdecay = False
            self._introframes = 0
        else:
            self._introlen = definition['buildup']['length'] if 'length' in definition['buildup'] else 0.0
            self._introcurve = definition['buildup']['curve'] if 'curve' in definition['buildup'] else 1.0
            self._introdecay = definition['buildup']['decays'] if 'decays' in definition['buildup'] else False
            self._introframes = int(self._introlen * self._fps)
        if 'cutaway' not in definition:
            self._cutlen = 0.0
            self._cutcurve = 1.0
            self._cutframes = 0
        else:
            self._cutlen = definition['cutaway']['length'] if 'length' in definition['cutaway'] else 0.0
            self._cutcurve = definition['cutaway']['curve'] if 'curve' in definition['cutaway'] else 1.0
            self._cutframes = int(self._cutlen * self._fps)
        if 'waves' in definition:
            self._waves = definition['waves']
        else:
            self._waves = []
            for wavetype in ['sine', 'triangle', 'sawtooth', 'square']:
                if wavetype in definition:
                    w = definition[wavetype]['weight'] if 'weight' in definition[wavetype] else 1.0
                    if 'harmonics' in definition[wavetype]:
                        for i in range(len(definition[wavetype]['harmonics'])):
                            harmonic_str = 10 ** (definition[wavetype]['harmonics'][i]/10)
                            self._waves.append({'type': wavetype, 'harmonic': i+1, 'weight': w*harmonic_str})
                    if 'overtones' in definition[wavetype]:
                        for mult in definition[wavetype]['overtones']:
                            overtone = definition[wavetype]['overtones'][mult]
                            harmonic_str = 10 ** (overtone/10)
                            self._waves.append({'type': wavetype, 'harmonic': float(mult), 'weight': w*harmonic_str})
        denom = sum([x['weight'] for x in self._waves])
        for wave in self._waves:
            wave['weight'] /= denom
    def _buildup_mult(self, fidx): 
        ftime = fidx / self._fps
        if ftime >= self._introlen:  #  TODO: test, but I don't think this is necessary with the min() on the return (same for self._cut_mult())
            return 1.0
        x = ftime / self._introlen
        return min(1.0, x ** self._introcurve)
    def _decay_mult(self, fidx):
        dtime = fidx / self._fps 
        if not self._introdecay:
            dtime -= self._introlen
        if dtime <= 0:
            return 1.0
        x = dtime / self._decaytime
        if self._decaytype == 'exponential':
            d = (1 - self._decayrate) ** x
        elif self._decaytype == 'linear':
            d = 1 - (x * self._decayrate)
        else:
            raise ValueError('Invalid decay type: "{0}"'.format(self._decaytype))
        return max(0, d)
    def _cut_mult(self, fnidx):
        cendtime = fnidx / self._fps 
        if cendtime > self._cutlen:
            return 1.0
        x = cendtime / self._cutlen
        return min(1.0, x ** self._cutcurve)
    #
    #  Waveform functions
    #  https://en.wikipedia.org/wiki/Waveform
    #
    def _sine(self, freq, fidx):
        return math.sin((2 * fidx * math.pi * freq) / self._fps)
    def _square(self, freq, fidx):
        return 1.0 if self._sine(freq, fidx) > 0.0 else -1.0 
    def _tri(self, freq, fidx):
        return (2/math.pi) * math.asin(math.sin((2 * fidx * math.pi * freq) / self._fps))
    def _saw(self, freq, fidx):
        return (2/math.pi) * math.atan(math.tan((fidx * math.pi * freq) / self._fps))
    def _wave(self, freq, mult, frame_count, wavefunc):
        subwave = []
        for i in range(frame_count):
            intro = self._buildup_mult(i) if i < self._introframes and not self._legato else 1
            decay = self._decay_mult(i) if self._decayrate > 0 else 1
            cut = self._cut_mult(frame_count-i) if not self._legato and frame_count-i < self._cutframes else 1
            legato = min(1, ((frame_count-i) / (self._fps / 32)) ** 0.5, (i / (self._fps / 32)) ** 0.5) if self._legato else 1
            wave = wavefunc(freq, i)
            if self._vibrato['cents'] > 0:
                basewave = wavefunc(freq, i)
                otherwave = wavefunc(freq + (2**(self._vibrato['cents']/1200)), i)
                vibwave = self._sine(self._vibrato['frequency'], i)
                vibf = (vibwave+1.0) / 2.0
                wave = (vibf * basewave) + ((1-vibf) * otherwave)
            if self._tremolo['drop'] > 0:
                basedyn = self.volume()
                lowdyn = self.volume() - self._tremolo['drop']
                tremwave = self._sine(self._tremolo['frequency'], i)
                tremf = (tremwave+1.0) / 2.0
                volume = (tremf * basedyn) + ((1-tremf) * lowdyn)
            else:
                volume = self.volume()
            v = wave * volume * mult * intro * decay * cut * legato
            subwave.append(v)
        return subwave
    def volume(self):
        return self._volume
    def set_volume(self, volume):
        if 0 < volume <= 1:
            self._volume = volume
    def legato(self):
        return self._legato
    def set_legato(self, islegato):
        """
        if not self._legato and islegato:
            self._origcutframes = self._cutframes
            self._origcutcurve = self._cutcurve
            self._cutframes = int(self._fps / 50)
            self._cutcurve = 1.0
        elif self._legato and not islegato:
            self._cutframes = self._origcutframes
            self._cutcurve = self._origcutcurve
        """
        self._legato = islegato
    def fps(self):
        return self._fps
    def set_fps(self, fps):
        self._fps = fps
    def name(self):
        return self._name
    def play_note(self, frequency, frame_count):
        frame_count = int(frame_count)
        fullwave = [0 for _ in range(frame_count)]
        for wave in self._waves:
            wavefunc = self._wf[wave['type']]
            subwave = self._wave(frequency*wave['harmonic'], 32767*wave['weight'], frame_count, wavefunc)
            fullwave = [fullwave[x]+subwave[x] for x in range(len(subwave))]
        return fullwave