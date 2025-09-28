from PyQt6 import QtCore, QtWidgets, QtMultimedia
import ndspy.soundArchive, audioop, wave, io#, pyaudio # audioop-lts

def play(audioBuffer: QtCore.QIODevice, sseq: ndspy.soundArchive.soundSequence.SSEQ, sdat: ndspy.soundArchive.SDAT):
    sseq.parse()
    if not sseq.parsed:
        print("Unable to parse sequence")
        return
    bank = sdat.banks[sseq.bankID][1]
    pcm_list = loadBank(bank, sdat)
    print(sseq.events)
    pcm = bytearray()
    for p in pcm_list:
        pcm += p
    audioBuffer.close()
    audioBuffer.setData(pcm)
    audioBuffer.open(QtCore.QBuffer.OpenModeFlag.ReadWrite)
    audioFormat = QtMultimedia.QAudioFormat()
    audioFormat.setChannelCount(1)
    audioFormat.setSampleFormat(audioFormat.SampleFormat.Int16)
    audioFormat.setSampleRate(22050)
    audioSink = QtMultimedia.QAudioSink(audioFormat, audioBuffer)
    audioSink.setVolume(0.2)
    audioSink.start(audioBuffer)
    while audioSink.state() == QtMultimedia.QAudio.State.ActiveState:
        print("yo")

def loadBank(bank: ndspy.soundArchive.soundBank.SBNK, sdat: ndspy.soundArchive.SDAT):
    pcm_list: list[bytes] = []
    swar_list: list = []
    for s in bank.waveArchiveIDs:
        swar_list.append(sdat.waveArchives[s][1])
    for i in bank.instruments:
        print(i)
        if isinstance(i, ndspy.soundArchive.soundBank.SingleNoteInstrument):
            print(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID])
            pcm_list.append(loadSWAV(swar_list[i.noteDefinition.waveArchiveIDID].waves[i.noteDefinition.waveID]))
        else:
            pcm_list.append(bytes())
    return pcm_list

def loadSWAV(snd_data: ndspy.soundArchive.soundWaveArchive.soundWave.SWAV):
    if snd_data.waveType == ndspy.soundArchive.soundWaveArchive.soundWave.WaveType.ADPCM:
        pcm_data, _ = audioop.adpcm2lin(snd_data.save(), 2, None)
    else:
        pcm_data = snd_data.save()
    pcm_file = io.BytesIO(pcm_data)
    wav = wave.open(pcm_file, "wb")
    wav.setparams((1, 2, snd_data.sampleRate, snd_data.totalLength, 'NONE', 'NONE'))
    wav.writeframes(pcm_data)
    return pcm_file.getvalue()