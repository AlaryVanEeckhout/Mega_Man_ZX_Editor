try:
    import sounddevice
except OSError:
    print("PortAudio library not found")
    raise ImportError # trigger the except block from sdat instead of actually crashing
import numpy
import ndspy.soundArchive as sa
from timeit import default_timer as timer
import threading
from .sdat import Sample

class WAVPlayer:
    def __init__(self, sample: Sample, samplerate: int, stop_on_note_end: bool=True):
        self.sample = sample
        assert len(sample.data.shape) == 1
        self.current_frame = 0
        self.stop_on_note_end = stop_on_note_end
        self.duration = None
        self.stream = sounddevice.OutputStream(
            samplerate=samplerate, 
            dtype="int16", 
            callback=self.callback,
        )
    

    def callback(self, outdata: numpy.ndarray, frames: int, time, status: sounddevice.CallbackFlags) -> None:
        is_note_end = False
        # try filling outdata with data
        range_start = self.current_frame
        range_end = self.current_frame+frames
        if self.duration is not None:
            range_start = min(range_start, self.duration)
            range_end = min(range_end, self.duration)
        mono_outdata = self.sample.get_data_range(range_start, range_end)
        if mono_outdata.shape[0] < frames:
            mono_outdata = numpy.append(mono_outdata, numpy.zeros((frames-mono_outdata.shape[0]), dtype="int16"))
        self.current_frame += mono_outdata.shape[0]

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
        super().__init__(sample=Sample(numpy.zeros((1000), dtype="int16"), None, 8000), samplerate=samplerate, stop_on_note_end=False)
    
    def play_note(self, event:sa.soundSequence.NoteSequenceEvent, sample:Sample, duration:int):
        speed_factor = 2.0 ** ((event.pitch-60) / 12.0)
        self.sample = sample.zoom(speed_factor) # speed/pitch adjust
        self.sample.data = numpy.astype((numpy.astype(self.sample.data, numpy.int32) * event.velocity) // 127, numpy.int16)
        self.duration = duration
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
        self.exit_flag = None

    def get_bpm_tick(self):
        return BPM_TICK_FACTOR / self.tempo
    
    def callback(self):
        self.event_time_last = timer()
        self.players.clear()
        self.players.append(NotePlayer(self.SAMPLERATE))
        self.players[0].play()
        print(f"Event Index {self.event_index}")
        while self.loop or self.event_index < len(self.events):
            self.event_time = timer()
            if self.event_time-self.event_time_last >= self.event_time_targetDelta:
                self.event_time_last += self.event_time_targetDelta
                self.event_time_targetDelta = 0
            while self.event_time_targetDelta == 0:
                event = self.events[self.event_index]
                pcm = self.pcm_list[self.pcm_index]
                if isinstance(event, sa.soundSequence.NoteSequenceEvent):
                    if pcm is not None:
                        duration = int(self.get_bpm_tick()*event.duration*self.SAMPLERATE) # for sample array
                        #print(event.duration)
                        self.players[0].play_note(event, pcm, duration)
                elif isinstance(event, sa.soundSequence.RestSequenceEvent):
                    # not actually a musical rest, how long to stop parsing events and let music play
                    # only this instruction sets event_time_targetDelta
                    self.event_time_targetDelta = self.get_bpm_tick()*event.duration
                elif isinstance(event, sa.soundSequence.InstrumentSwitchSequenceEvent):
                    self.pcm_index = event.instrumentID
                elif isinstance(event, sa.soundSequence.TempoSequenceEvent):
                    self.tempo = event.value
                    #print(f"tempo {self.tempo}")
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
            #print(f"exec time: {timer()-self.event_time}")
            self.exit_flag.wait(self.event_time_targetDelta-(timer()-self.event_time))

    def play(self):
        self.thread = threading.Thread(target=self.callback, daemon=True)
        self.exit_flag = threading.Event()
        self.thread.start()

    def stop(self):
        for player in self.players:
            player.stop()
        self.loop = False
        self.event_index = len(self.events)-1
        print("music stop")