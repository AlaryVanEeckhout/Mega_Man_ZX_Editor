global player
player = None
#https://problemkaputt.de/gbatek.htm#dssoundfilessseqsoundsequence
NDS_CPU_CLOCK = 33513982
TIMER_DIVIDER = 2728
SSEQ_CLOCK_FREQ = NDS_CPU_CLOCK/TIMER_DIVIDER
BPM_TICK_FACTOR = (64 * 240) / SSEQ_CLOCK_FREQ
try:
    import ndspy.soundArchive as sa, numpy, struct, audioop# audioop-lts
    import scipy.ndimage
    import math
    class Sample:
        def __init__(self, data: numpy.ndarray, loop: int, samplerate: int, notedef: sa.soundBank.NoteDefinition=None, pitch_change=True):
            self.data = data
            self.loop = loop
            self.samplerate = samplerate
            self.notedef = notedef
            self.pitch_change = pitch_change
            if self.notedef is not None: # adsr
                self.attack_coeff = self.get_attack_coeff()
                self.decay_rate = self.get_decay_rate()
                self.sustain_factor = self.get_sustain_factor()
                self.release_rate = self.get_release_rate()
        
        def __str__(self):
            type_names = {
                0: "none",
                1: "single-note PCM",
                2: "single-note PSG square wave",
                3: "single-note PSG white noise",
                16:"range",
                17:"regional",}
            return f"{type_names.get(self.notedef.type, hex(self.notedef.type))} {self.samplerate}Hz" + (f"  loop={self.loop}" if self.loop is not None else "") + ("" if self.pitch_change else "  single-pitch")
        
        def get_data_range(self, start, end):
            goal_len = end - start
            out = self.data[start:end]
            if self.loop is None or (self.data.shape[0]-self.loop) == 0:
                return numpy.append(out, numpy.zeros((goal_len-out.shape[0]), dtype=out.dtype))
            if start >= self.data.shape[0]:
                # starts in loop part, add first loop in loop part
                # let start == k+x*loop where loop <= k+loop < self.data.shape[0], then start_loop_space = k+loop
                start_loop_space = (start-self.loop) % (self.data.shape[0]-self.loop) + self.loop
                # subtract (x-1)*loop from end
                end -= start - start_loop_space
                # from here, end can be either less or greater than self.data.shape[0]
                # if it is less, it will skip the while
                # if it is greater, it will enter the while to concatenate the next loops
                out = numpy.concat((out, self.data[start_loop_space:end]))
            start = self.loop
            while out.shape[0] < goal_len:
                end -= self.data.shape[0] - self.loop
                out = numpy.concat((out, self.data[start:end]))
            return out
        
        def get_attack_coeff(self):
            assert self.notedef is not None
            if self.notedef.attack == 127: 
                return 0  # Instantaneous trigger
            # The official hardware table lookup calculation
            # Maps 0..127 into the DS engine cycle multiplier coefficient
            if self.notedef.attack < 100:
                return 255 - self.notedef.attack
            else:
                return (127 - self.notedef.attack) * 16
        
        def _get_linear_gain_slope(self, value):
            if value == 0: return 0
            # Decays and releases scale exponentially by powers of 2 in the hardware
            if value < 120:
                value2 = (value + 1) * 2
            else:
                value2 = (value - 119) * 256 + 240
            # Scale to the sequencer clock frequency
            value2 *= SSEQ_CLOCK_FREQ
            # *60 because 1 step = 60 ticks
            # 92544.0 converts raw hardware counter units into a meaningful rate
            return (value2 * 60) / 92544.0
            
        def get_decay_rate(self):
            assert self.notedef is not None
            return self._get_linear_gain_slope(self.notedef.decay)
        
        def get_release_rate(self):
            assert self.notedef is not None
            return self._get_linear_gain_slope(self.notedef.release)

        def get_sustain_factor(self):
            return 1 if self.notedef is None else (self.notedef.sustain / 127.0) ** 2
        
        def zoom(self, speed_factor):
            new_data = scipy.ndimage.zoom(self.data, 1 / speed_factor, order=0) # speed/pitch adjust
            new_loop = int(self.loop / speed_factor) if self.loop is not None else None
            new_sample = Sample(new_data, new_loop, self.samplerate, self.notedef, self.pitch_change)
            return new_sample
    from . import wav_player

    # samples for DS's PSG channels
    SQUARE_SAMPLE_DATA = [
        numpy.asarray(
            [1 if i+j >= 7 else -1 for j in range(8)], 
            dtype=numpy.int16
        ) * 0x7FFF
        for i in range(8)
    ]

    def playSSEQ(sseq: sa.soundSequence.SSEQ, sdat: sa.SDAT, trackButtons: list=None):
        global player
        stopSound()
        if not sseq.parsed:
            print("Unable to parse sequence")
            return
        bank = sdat.banks[sseq.bankID][1]
        sample_list = loadBank(bank, sdat)
        #print(sseq.events)
        #print(sseq.bankID)
        # todo: investigate playerID
        player = wav_player.SSEQPlayer(sseq.events, sample_list, trackButtons=trackButtons)
        player.play()

    def loadBank(bank: sa.soundBank.SBNK, sdat: sa.SDAT):
        sample_list: list[Sample] = []
        swar_list = get_swar_list(bank, sdat)
        for i in bank.instruments:
            sample_list.append(loadInstrument(i, swar_list))

        #print(sample_list)
        return sample_list
    
    def get_swar_list(bank: sa.soundBank.SBNK, sdat: sa.SDAT) -> list[sa.soundWaveArchive.SWAR]:
        swar_list = []
        for s in bank.waveArchiveIDs:
            swar_list.append(sdat.waveArchives[s][1]) # object is at index 1
        return swar_list

    def loadInstrument(i: sa.soundBank.Instrument, swar_list: list[sa.soundWaveArchive.SWAR]) -> Sample | list[Sample] | None:
        #print(i)
        if isinstance(i, sa.soundBank.SingleNoteInstrument):
            #print(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID])
            if i.type == sa.soundBank.SINGLE_NOTE_PCM_INSTRUMENT_TYPE:
                return loadSWAV(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID], i.noteDefinition)
            elif i.type == sa.soundBank.SINGLE_NOTE_PSG_SQUARE_WAVE_INSTRUMENT_TYPE:
                sample = Sample(SQUARE_SAMPLE_DATA[i.noteDefinition.dutyCycle], loop=0, samplerate=int(440 * 2**(-3/4) * 8), notedef=i.noteDefinition)
                return sample
        elif isinstance(i, sa.soundBank.RangeInstrument):
            # contains one instrument per pitch in a certain range
            sample_range = []
            for d in range(128):
                if d < i.firstPitch or d-i.firstPitch > len(i.noteDefinitions)-1:
                    sample_range.append(None)
                else:
                    noteDefinition = i.noteDefinitions[d-i.firstPitch]
                    sample = loadSWAV(swar_list[noteDefinition.waveArchiveIDID].waves[noteDefinition.waveID], noteDefinition)
                    sample.pitch_change = False
                    sample_range.append(sample)
            assert len(sample_range) == 128
            return sample_range
        elif isinstance(i, sa.soundBank.RegionalInstrument):
            # like RangeInstrument, but an intrument is reused for multiple pitchs (region)
            sample_range = []
            for d in range(128):
                for r in i.regions:
                    if r.lastPitch > len(sample_range): # assuming that all regions are sorted in ascending lastPitch order
                        sample_range.append(loadSWAV(swar_list[r.noteDefinition.waveArchiveIDID].waves[r.noteDefinition.waveID], r.noteDefinition))
                        break
                if len(sample_range) <= d:
                    sample_range.append(None)
            assert len(sample_range) == 128
            return sample_range
        else:
            return None

    def loadSWAV(swav: sa.soundWaveArchive.soundWave.SWAV, notedef: sa.soundBank.NoteDefinition=None):
        assert type(swav) == sa.soundWaveArchive.soundWave.SWAV
        if swav.waveType == sa.soundWaveArchive.soundWave.WaveType.ADPCM:
            # DS uses Low-Nibble first; audioop expects High-Nibble first.
            state = struct.unpack('<hB', swav.data[:3]) # Parse the 4-byte ADPCM Header
            data_np = numpy.frombuffer(swav.data[4:], dtype="uint8")
            adpcm_data = ((data_np & 0x0F) << 4) | ((data_np & 0xF0) >> 4)

            pcm_data = numpy.frombuffer(audioop.adpcm2lin(adpcm_data, 2, state)[0], dtype="int16") * 1
        else: #PCM8 or PCM16
            pcm_data = numpy.frombuffer(swav.data, dtype="int16")
        loop = (swav.loopOffset-1)*8 if swav.isLooped else None
        return Sample(pcm_data, loop, swav.sampleRate, notedef)

    # Intended for playback of individual SWAVs. Volume reduced to reasonable value.
    def playSWAV(swav: sa.soundWaveArchive.soundWave.SWAV):
        global player
        stopSound()
        print(f"Wave type: {swav.waveType.name}")
        print(f"Sample rate: {swav.sampleRate}")
        sample = loadSWAV(swav)
        sample.data //= 5 # reduce sound volume to something reasonable
        player = wav_player.WAVPlayer([sample])
        player.play()

    def stopSound():
        global player
        if player is not None:
            player.stop()

except ImportError as e:
    print("Dependencies for audio playback are not met. Functions are disabled.")
    def playSSEQ(*args, **kwargs): return
    def playSWAV(*args, **kwargs): return
    def stopSound(*args, **kwargs): return
    def plotSound(*args, **kwargs): return