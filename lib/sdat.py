global player
player = None
try:
    import ndspy.soundArchive as sa, numpy, struct, audioop# audioop-lts
    import scipy.ndimage
    class Sample:
        def __init__(self, data: numpy.ndarray, loop: int, samplerate: int, notedef: sa.soundBank.NoteDefinition=None, pitch_change=True):
            self.data = data
            self.loop = loop
            self.samplerate = samplerate
            self.notedef = notedef
            self.pitch_change = pitch_change
        
        def get_data_range(self, start, end):
            goal_len = end - start
            out = self.data[start:end]
            if not self.loop:
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
        
        def zoom(self, speed_factor):
            new_data = scipy.ndimage.zoom(self.data, 1 / speed_factor, order=0) # speed/pitch adjust
            new_loop = int(self.loop / speed_factor) if self.loop is not None else None
            new_sample = Sample(new_data, new_loop, self.samplerate, self.notedef, self.pitch_change)
            return new_sample
    from . import wav_player


            

    def playSSEQ(sseq: sa.soundSequence.SSEQ, sdat: sa.SDAT):
        global player
        stopSound()
        sseq.parse()
        if not sseq.parsed:
            print("Unable to parse sequence")
            return
        bank = sdat.banks[sseq.bankID][1]
        sample_list = loadBank(bank, sdat)
        print(sseq.events)
        #print(sseq.bankID)
        player = wav_player.SSEQPlayer(sseq.events, sample_list)
        player.play()

    def loadBank(bank: sa.soundBank.SBNK, sdat: sa.SDAT):
        sample_list: list[Sample] = []
        swar_list: list = []
        for s in bank.waveArchiveIDs:
            swar_list.append(sdat.waveArchives[s][1])
        for i in bank.instruments:
            #print(i)
            if isinstance(i, sa.soundBank.SingleNoteInstrument):
                #print(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID])
                sample_list.append(loadSWAV(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID], i.noteDefinition))
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
                sample_list.append(sample_range)
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
                sample_list.append(sample_range)
            else:
                sample_list.append(None)
        print(sample_list)
        return sample_list

    def loadSWAV(swav: sa.soundWaveArchive.soundWave.SWAV, notedef: sa.soundBank.NoteDefinition=None):
        assert type(swav) == sa.soundWaveArchive.soundWave.SWAV
        if swav.waveType == sa.soundWaveArchive.soundWave.WaveType.ADPCM:
            # DS uses Low-Nibble first; audioop expects High-Nibble first.
            state = struct.unpack('<hB', swav.data[:3]) # Parse the 4-byte ADPCM Header
            data_np = numpy.frombuffer(swav.data[4:], dtype="uint8")
            adpcm_data = ((data_np & 0x0F) << 4) | ((data_np & 0xF0) >> 4)

            pcm_data = numpy.frombuffer(audioop.adpcm2lin(adpcm_data, 2, state)[0], dtype="int16") * -1
        else: #PCM8 or PCM16
            pcm_data = numpy.fromiter(swav.data, dtype="int16")
        loop = (swav.loopOffset-1)*8 if swav.isLooped else None
        return Sample(pcm_data, loop, swav.sampleRate, notedef)

    # Intended for playback of individual SWAVs. Volume reduced to reasonable value.
    def playSWAV(swav: sa.soundWaveArchive.soundWave.SWAV):
        global player
        stopSound()
        print(f"Wave type: {swav.waveType.name}")
        print(f"Sample rate: {swav.sampleRate}")
        sample = loadSWAV(swav)
        #sample.data //= 5
        player = wav_player.WAVPlayer(sample)
        player.play()

    def stopSound():
        global player
        if player is not None:
            player.stop()

except ImportError:
    print("Dependencies for audio playback are not met. Functions are disabled.")
    def playSSEQ(*args, **kwargs): return
    def playSWAV(*args, **kwargs): return
    def stopSound(*args, **kwargs): return
    def plotSound(*args, **kwargs): return