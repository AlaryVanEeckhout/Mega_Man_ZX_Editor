try:
    import sounddevice
except OSError:
    print("PortAudio library not found")
    raise ImportError # trigger the except block from sdat instead of actually crashing
import numpy, scipy.ndimage
import ndspy.soundArchive as sa
from timeit import default_timer as timer
import threading

class WAVPlayer:
    def __init__(self, data: numpy.ndarray, samplerate: int, loop: int=None, stop_on_note_end: bool=True):
        self.data = data # 1d array
        assert len(data.shape) == 1
        self.loop = loop
        self.current_frame = 0
        self.stop_on_note_end = stop_on_note_end
        self.stream = sounddevice.OutputStream(
            samplerate=samplerate, 
            dtype="int16", 
            callback=self.callback,
        )
    

    def callback(self, outdata: numpy.ndarray, frames: int, time, status: sounddevice.CallbackFlags) -> None:
        is_note_end = False
        # try filling outdata with data
        mono_outdata = self.data[self.current_frame:self.current_frame+frames]
        self.current_frame += mono_outdata.shape[0]

        # if outdata is not full, it must be bc we reached the end of data before the end of outdata
        while mono_outdata.shape[0] < frames:
            frames_remaining = frames-mono_outdata.shape[0]
            if self.loop is None:
                # no loop, pad the rest of outdata with zero and stop stream
                is_note_end = True
                mono_outdata = numpy.append(mono_outdata, numpy.zeros((frames_remaining), dtype="int16"))
            else:
                # loop, continue filling outdata with data starting from the loop point
                self.current_frame = self.loop*8
                add_mono_outdata = self.data[self.current_frame:self.current_frame+frames_remaining]
                self.current_frame += add_mono_outdata.shape[0]
                mono_outdata = numpy.append(mono_outdata, add_mono_outdata)
        #print(mono_outdata)
        # fill stereo outdata
        for i in range(outdata.shape[1]):
            outdata[:, i] = mono_outdata
        # stop stream if at the end
        if is_note_end and self.stop_on_note_end:
            print("stop")
            raise sounddevice.CallbackStop
    

    def play(self):
        self.stream.start()
    

    def stop(self):
        self.stream.abort()

class NotePlayer(WAVPlayer):
    def __init__(self, samplerate):
        super().__init__(data=numpy.zeros((1000), dtype="int16"), samplerate=samplerate, loop=None, stop_on_note_end=False)
    
    def play_note(self, event:sa.soundSequence.NoteSequenceEvent, pcm:numpy.ndarray, duration:int):
        speed_factor = 2.0 ** ((event.pitch-60) / 12.0)
        pcm_new = scipy.ndimage.zoom(pcm, 1 / speed_factor, order=0) # speed/pitch adjust
        self.data = pcm_new[:duration]
        self.current_frame = 0

#https://problemkaputt.de/gbatek.htm#dssoundfilessseqsoundsequence
BPM_TICK_FACTOR = (64*2728/33000000) * 240

class SSEQPlayer:
    def __init__(self, events: list[sa.soundSequence.SequenceEvent], pcm_list:list[numpy.ndarray], samplerate: int, loop: int=None):
        self.SAMPLERATE = samplerate
        self.events = events
        self.pcm_list = pcm_list
        self.loop = loop
        self.tempo = 150
        self.pcm_index = 0
        self.event_index = 0
        self.event_time = 0
        self.event_time_last = 0
        self.event_time_targetDelta = 0
        self.players: list[NotePlayer] = []
        self.thread = None

    def get_bpm_tick(self):
        return BPM_TICK_FACTOR / self.tempo

    def play(self):
        def callback():
            self.event_time_last = timer()
            self.players.clear()
            self.players.append(NotePlayer(self.SAMPLERATE))
            self.players[0].play()
            while self.loop or self.event_index < len(self.events):
                self.event_time = timer()
                if self.event_time-self.event_time_last >= self.event_time_targetDelta:
                    self.event_time_last += self.event_time_targetDelta
                    self.event_time_targetDelta = 0
                    self.players[0].data = numpy.zeros((1000), dtype="int16") # the qty of zeros is not important
                while self.event_time_targetDelta == 0:
                    event = self.events[self.event_index]
                    pcm = self.pcm_list[self.pcm_index]
                    if isinstance(event, sa.soundSequence.NoteSequenceEvent):
                        if pcm is not None:
                            duration = int(self.get_bpm_tick()*event.duration*self.SAMPLERATE) # for sample array
                            print(event.duration)
                            self.players[0].play_note(event, pcm, duration)
                    elif isinstance(event, sa.soundSequence.RestSequenceEvent):
                        # not actually a musical rest, how long to stop parsing events and let music play
                        # only this instruction sets event_time_targetDelta
                        duration = int(self.get_bpm_tick()*event.duration*self.SAMPLERATE)
                        self.event_time_targetDelta = self.get_bpm_tick()*event.duration
                    elif isinstance(event, sa.soundSequence.InstrumentSwitchSequenceEvent):
                        self.pcm_index = event.instrumentID
                    elif isinstance(event, sa.soundSequence.TempoSequenceEvent):
                        self.tempo = event.value
                    elif isinstance(event, sa.soundSequence.BeginTrackSequenceEvent):
                        pass # Instantiate WAVPlayers here
                    event_name = ""
                    if hasattr(event, "name"):
                        event_name = event.name
                    print(f"{event_name} (event {self.event_index}/{len(self.events)-1}) tempo {self.tempo} tdelta {self.event_time_targetDelta}")
                    self.event_index += 1
                    if self.event_index > len(self.events)-1:
                        self.stop()
                        return
                self.event_time += 1
        self.thread = threading.Thread(target=callback)
        self.thread.start()

    def stop(self):
        for player in self.players:
            player.stop()
        self.loop = False
        self.event_index = len(self.events)-1