try:
    import ndspy.soundArchive as sa, numpy, struct, audioop# audioop-lts
    from . import wav_player

    global player
    player = None

    def playSSEQ(sseq: sa.soundSequence.SSEQ, sdat: sa.SDAT):
        global player
        stopSound()
        sseq.parse()
        if not sseq.parsed:
            print("Unable to parse sequence")
            return
        bank = sdat.banks[sseq.bankID][1]
        pcm_list = loadBank(bank, sdat)
        print(sseq.events)
        #print(sseq.bankID)
        player = wav_player.SSEQPlayer(sseq.events, pcm_list, 22050, None)
        player.play()

    def loadBank(bank: sa.soundBank.SBNK, sdat: sa.SDAT):
        pcm_list: list[numpy.ndarray] = []
        swar_list: list = []
        for s in bank.waveArchiveIDs:
            swar_list.append(sdat.waveArchives[s][1])
        for i in bank.instruments:
            print(i)
            if isinstance(i, sa.soundBank.SingleNoteInstrument):
                #print(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID])
                pcm_list.append(loadSWAV(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID]))
            elif isinstance(i, sa.soundBank.RangeInstrument):
                pass
                pcm_list.append(None)
            elif isinstance(i, sa.soundBank.RegionalInstrument):
                pass
                pcm_list.append(None)
            else:
                pass
                pcm_list.append(None)
        return pcm_list

    def loadSWAV(swav: sa.soundWaveArchive.soundWave.SWAV):
        assert type(swav) == sa.soundWaveArchive.soundWave.SWAV
        if swav.waveType == sa.soundWaveArchive.soundWave.WaveType.ADPCM:
            # DS uses Low-Nibble first; audioop expects High-Nibble first.
            state = struct.unpack('<hB', swav.data[:3]) # Parse the 4-byte ADPCM Header
            data_np = numpy.frombuffer(swav.data[4:], dtype="uint8")
            adpcm_data = ((data_np & 0x0F) << 4) | ((data_np & 0xF0) >> 4)

            pcm_data = numpy.frombuffer(audioop.adpcm2lin(adpcm_data, 2, state)[0], dtype="int16") * -1
        else: #PCM8 or PCM16
            pcm_data = swav.data
        return numpy.fromiter(pcm_data, dtype="int16")

    # Intended for playback of individual SWAVs. Volume reduced to reasonable value.
    def playSWAV(swav: sa.soundWaveArchive.soundWave.SWAV):
        global player
        stopSound()
        print(f"Wave type: {swav.waveType.name}")
        print(f"Sample rate: {swav.sampleRate}")
        player = wav_player.WAVPlayer(loadSWAV(swav) // 5, swav.sampleRate, swav.loopOffset-1 if swav.isLooped else None, swav.totalLength)
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