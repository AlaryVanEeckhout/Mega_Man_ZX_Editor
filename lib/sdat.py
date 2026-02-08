try:
    from PyQt6 import QtCore, QtWidgets#, QtMultimedia
    import ndspy.soundArchive, audioop, numpy# audioop-lts
    from . import wav_player

    global player
    player = None

    def playSSEQ(sseq: ndspy.soundArchive.soundSequence.SSEQ, sdat: ndspy.soundArchive.SDAT):
        sseq.parse()
        if not sseq.parsed:
            print("Unable to parse sequence")
            return
        bank = sdat.banks[sseq.bankID][1]
        pcm_list = loadBank(bank, sdat)
        #print(sseq.events)
        print(sseq.bankID)

    def loadBank(bank: ndspy.soundArchive.soundBank.SBNK, sdat: ndspy.soundArchive.SDAT):
        pcm_list: list[numpy.ndarray] = []
        swar_list: list = []
        for s in bank.waveArchiveIDs:
            swar_list.append(sdat.waveArchives[s][1])
        for i in bank.instruments:
            print(i)
            if isinstance(i, [ndspy.soundArchive.soundBank.SingleNoteInstrument]):
                print(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID])
                pcm_list.append(loadSWAV(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID]))
            else:
                pcm_list.append(None)
        return pcm_list

    def loadSWAV(snd_data: ndspy.soundArchive.soundWaveArchive.soundWave.SWAV):
        assert type(snd_data) == ndspy.soundArchive.soundWaveArchive.soundWave.SWAV
        if snd_data.waveType == ndspy.soundArchive.soundWaveArchive.soundWave.WaveType.ADPCM:
            pcm_data, _ = audioop.adpcm2lin(snd_data.save()[-snd_data.totalLength*4:], 2, None)
        else:
            print("audio data was not converted")
            pcm_data = snd_data.save()
        return numpy.frombuffer(pcm_data, dtype="int16")

    # Intended for playback of individual SWAVs. Volume reduced to reasonable value.
    def playSWAV(snd_data: ndspy.soundArchive.soundWaveArchive.soundWave.SWAV):
        stopSound()
        print(f"sample rate: {snd_data.sampleRate}")
        global player
        player = wav_player.WAVPlayer(loadSWAV(snd_data), snd_data.sampleRate, snd_data.loopOffset if snd_data.isLooped else None, snd_data.totalLength)
        player.play()

    def stopSound():
        global player
        if player is not None:
            player.stop()

except ImportError:
    print("dependencies for audio playback are not met. functions are disabled.")
    def playSSEQ(*args, **kwargs): return
    def playSWAV(*args, **kwargs): return
    def stopSound(*args, **kwargs): return
    def plotSound(*args, **kwargs): return