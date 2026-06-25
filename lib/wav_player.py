try:
    import sounddevice
except OSError:
    print("PortAudio library not found")
    raise ImportError # trigger the except block from sdat instead of actually crashing
import numpy, scipy.ndimage
import ndspy.soundArchive as sa
from timeit import default_timer as timer

class WAVPlayer:
    def __init__(self, data: numpy.ndarray, samplerate: int, loop: int|None, totalLen:int=None):
        self.data = data # 1d array
        assert len(data.shape) == 1
        self.loop = loop
        self.current_frame = 0
        self.totalLen = totalLen # for debug purposes
        self.stream = sounddevice.OutputStream(
            samplerate=samplerate, 
            dtype="int16", 
            callback=self.callback,
        )
    

    def callback(self, outdata: numpy.ndarray, frames: int, time, status: sounddevice.CallbackFlags) -> None:
        callback_stop = False
        # try filling outdata with data
        mono_outdata = self.data[self.current_frame:self.current_frame+frames]
        self.current_frame += mono_outdata.shape[0]

        # if outdata is not full, it must be bc we reached the end of data before the end of outdata
        while mono_outdata.shape[0] < frames:
            frames_remaining = frames-mono_outdata.shape[0]
            if self.loop is None:
                # no loop, pad the rest of outdata with zero and stop stream
                callback_stop = True
                mono_outdata = numpy.append(mono_outdata, numpy.zeros((frames_remaining), dtype="int16"))
            else:
                # loop, continue filling outdata with data starting from the loop point
                self.current_frame = self.loop*8
                add_mono_outdata = self.data[self.current_frame:self.current_frame+frames_remaining]
                self.current_frame += add_mono_outdata.shape[0]
                mono_outdata = numpy.append(mono_outdata, add_mono_outdata)
        #print(len(self.data), self.totalLen)
        #print(mono_outdata)
        # fill stereo outdata
        for i in range(outdata.shape[1]):
            outdata[:, i] = mono_outdata
        # stop stream if at the end
        if callback_stop:
            raise sounddevice.CallbackStop
    

    def play(self):
        self.stream.start()
    

    def stop(self):
        self.stream.abort()

#https://problemkaputt.de/gbatek.htm#dssoundfilessseqsoundsequence
BPM_TICK_FACTOR = (64*2728/33000000) * 240

class SSEQPlayer(WAVPlayer): # To do : Make this player command multiple WAVPlayers for the tracks instead of being one WAVPlayer
    def __init__(self, events: list[sa.soundSequence.SequenceEvent], pcm_list:list[numpy.ndarray], samplerate: int, loop: int|None, totalLen:int=None):
        self.SAMPLERATE = samplerate
        self.events = events
        self.pcm_list = pcm_list
        self.tempo = 150
        self.pcm_index = 0
        self.event_index = 0
        self.event_time = 0
        self.event_time_last = 0
        self.event_time_targetDelta = 0
        self.data = numpy.zeros(1000, dtype="int16")
        super().__init__(self.data, self.SAMPLERATE, loop, totalLen)

    def get_bpm_tick(self):
        return BPM_TICK_FACTOR / self.tempo

    def callback(self, outdata, frames, time, status):
        callback_stop = False
        self.event_time = timer()
        if self.event_time-self.event_time_last >= self.event_time_targetDelta:
            self.event_time_last += self.event_time_targetDelta
            self.event_time_targetDelta = 0
            self.data = numpy.zeros((1000), dtype="int16") # the qty of zeros is not important
        while self.event_time_targetDelta == 0:
            event = self.events[self.event_index]
            pcm = self.pcm_list[self.pcm_index]
            if isinstance(event, sa.soundSequence.NoteSequenceEvent):
                if pcm is not None:
                    speed_factor = 2.0 ** ((event.pitch-60) / 12.0)
                    pcm_new = scipy.ndimage.zoom(pcm, 1 / speed_factor, order=0) # speed/pitch adjust
                    duration = int(self.get_bpm_tick()*event.duration*self.SAMPLERATE) # for sample array
                    print(event.duration)
                    self.data = pcm_new[:duration]
                    self.current_frame = 0 # play sound from start
            elif isinstance(event, sa.soundSequence.RestSequenceEvent):
                # not actually a musical rest, how long to stop parsing events and let music play
                # only this instruction sets event_time_targetDelta
                duration = int(self.get_bpm_tick()*event.duration*self.SAMPLERATE)
                self.event_time_targetDelta = self.get_bpm_tick()*event.duration
                self.current_frame = 0
            elif isinstance(event, sa.soundSequence.InstrumentSwitchSequenceEvent):
                self.pcm_index = event.instrumentID
            elif isinstance(event, sa.soundSequence.TempoSequenceEvent):
                self.tempo = event.value
            print(f"{event.name} (event {self.event_index}/{len(self.events)-1}) tempo {self.tempo} tdelta {self.event_time_targetDelta}")
            if self.loop is None and self.event_index >= len(self.events)-1:
                callback_stop = True
                break
            self.event_index += 1

        # try filling outdata with data
        mono_outdata = self.data[self.current_frame:self.current_frame+frames]
        self.current_frame += mono_outdata.shape[0]

        # if outdata is not full, it must be bc we reached the end of data before the end of outdata
        while mono_outdata.shape[0] < frames:
            frames_remaining = frames-mono_outdata.shape[0]
            if self.loop is None:
                # no loop, pad the rest of outdata with zero and stop stream
                mono_outdata = numpy.append(mono_outdata, numpy.zeros((frames_remaining), dtype="int16"))
            else:
                # loop, continue filling outdata with data starting from the loop point
                self.current_frame = self.loop*8
                add_mono_outdata = self.data[self.current_frame:self.current_frame+frames_remaining]
                self.current_frame += add_mono_outdata.shape[0]
                mono_outdata = numpy.append(mono_outdata, add_mono_outdata)
        #print(len(self.data), self.totalLen)
        #print(mono_outdata)
        # fill stereo outdata
        for i in range(outdata.shape[1]):
            outdata[:, i] = mono_outdata
        # stop stream if at the end
        if callback_stop:
            print("Stream stop")
            raise sounddevice.CallbackStop
        self.event_time += 1
    
    def play(self):
        super().play()
        self.event_time_last = timer()