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
    def __init__(self, sample: Sample, stop_on_note_end: bool=True):
        STREAM_SAMPLERATE = 22050
        self.sample = sample.zoom(sample.samplerate/STREAM_SAMPLERATE) # resample
        assert len(sample.data.shape) == 1
        self.current_frame = 0
        self.stop_on_note_end = stop_on_note_end
        self.duration = None
        self.stream = sounddevice.OutputStream(
            samplerate=STREAM_SAMPLERATE,  # samplerate cannot change after being set
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
    def __init__(self):
        super().__init__(sample=Sample(numpy.zeros((1000), dtype="int16"), None, 8000), stop_on_note_end=False)
    
    def play_note(self, event:sa.soundSequence.NoteSequenceEvent, sample:Sample, duration:int):
        #self.sample = sample.zoom(self.sample.samplerate/self.stream.samplerate) # resample
        speed_factor = 2.0 ** ((event.pitch-60) / 12.0)
        self.sample = sample.zoom(speed_factor) # speed/pitch adjust
        self.sample.data = numpy.astype((numpy.astype(self.sample.data, numpy.int32) * event.velocity) // 127, numpy.int16)
        self.duration = duration
        self.current_frame = 0

#https://problemkaputt.de/gbatek.htm#dssoundfilessseqsoundsequence
BPM_TICK_FACTOR = (64*2728/33000000) * 240

class SSEQPlayer:
    def __init__(self, events: list[sa.soundSequence.SequenceEvent], sample_list:list[Sample], loop: int=None):
        self.events = events
        self.sample_list = sample_list
        self.loop = loop # should this exist?
        self.tempo = 150
        self.TRACKS_MAX = 16 # IDs 0 to 15
        self.tracks = max(self.events[0].trackNumbers)+1 # used to create lists, skipped IDs are just ignored
        self.sample_indexes: list[int] = [0]*self.tracks # index into bank instruments
        self.event_indexes: list[int] = [0]*self.tracks
        self.event_times: list[int] = [0]*self.tracks # current time
        self.event_times_last: list[int] = [0]*self.tracks # time from previous wait
        self.event_times_targetDelta: list[int] = [0]*self.tracks # target waiting time
        self.return_indexes: list[int] = [0]*self.tracks # used with call and return events
        self.tracks_finished: list[bool] = [False]*self.tracks
        self.track_current = 0
        self.players: list[NotePlayer] = [None]*self.tracks
        self.thread = None
        self.exit_flag = None

    def get_bpm_tick(self):
        return BPM_TICK_FACTOR / self.tempo
    
    def next_track(self):
        # True = there is a next track, False = looping pack to 0 or remaining track
        try:
            assert any(x for x in self.events[0].trackNumbers if x != self.track_current and not self.tracks_finished[x]) # check that there are other tracks to go to
        except AssertionError:
            return False
        if self.track_current < self.tracks-1:
            try:
                self.track_current = min(x for x in self.events[0].trackNumbers if x > self.track_current and not self.tracks_finished[x]) # goto next track in set
                return True
            except ValueError:
                pass
        self.track_current = 0
        return False

    def callback(self):
        self.event_times_last = [timer()]*self.tracks
        self.players[0] = NotePlayer()
        self.players[0].play()
        while self.loop or self.tracks_finished.count(True) < len(self.events[0].trackNumbers):
            if self.players[self.track_current].stream.active == False:
                raise InterruptedError
            if self.tracks_finished[self.track_current]:
                print(f"moving from completed track {self.track_current}")
                self.next_track()
                print(f"to track {self.track_current}")
                print(self.tracks_finished)
                continue
            self.event_times[self.track_current] = timer()
            if self.event_times[self.track_current]-self.event_times_last[self.track_current] >= self.event_times_targetDelta[self.track_current]:
                self.event_times_last[self.track_current] += self.event_times_targetDelta[self.track_current]
                self.event_times_targetDelta[self.track_current] = 0
            while self.event_times_targetDelta[self.track_current] == 0:
                event = self.events[self.event_indexes[self.track_current]]
                sample = self.sample_list[self.sample_indexes[self.track_current]]
                if isinstance(event, sa.soundSequence.NoteSequenceEvent):
                    if sample is not None:
                        duration = int(self.get_bpm_tick()*event.duration*self.players[self.track_current].stream.samplerate) # for sample array
                        sample_selected = sample
                        if isinstance(sample, list):
                            sample_selected = sample[event.pitch]
                        if sample_selected is not None:
                            print(f"samplerate {sample_selected.samplerate}")
                            self.players[self.track_current].play_note(event, sample_selected, duration)
                elif isinstance(event, sa.soundSequence.RestSequenceEvent):
                    # not actually a musical rest, how long to stop parsing events and let music play
                    # only this instruction sets event_time_targetDelta
                    self.event_times_targetDelta[self.track_current] = self.get_bpm_tick()*event.duration
                    print(f"tdelta {self.event_times_targetDelta[self.track_current]}")
                elif isinstance(event, sa.soundSequence.InstrumentSwitchSequenceEvent):
                    self.sample_indexes[self.track_current] = event.instrumentID
                elif isinstance(event, sa.soundSequence.TempoSequenceEvent):
                    self.tempo = event.value
                elif isinstance(event, sa.soundSequence.CallSequenceEvent):
                    self.return_indexes[self.track_current] = self.event_indexes[self.track_current]
                    self.event_indexes[self.track_current] = next((i for i, obj in enumerate(self.events) if obj is event.destination))
                elif isinstance(event, sa.soundSequence.JumpSequenceEvent):
                    self.event_indexes[self.track_current] = next((i for i, obj in enumerate(self.events) if obj is event.destination))
                elif isinstance(event, sa.soundSequence.ReturnSequenceEvent):
                    self.event_indexes[self.track_current] = self.return_indexes[self.track_current]
                elif isinstance(event, sa.soundSequence.BeginTrackSequenceEvent): # For Tracks other than Track 0
                    self.event_indexes[event.trackNumber] = next((i for i, obj in enumerate(self.events) if obj is event.firstEvent))
                    self.return_indexes[event.trackNumber] = self.event_indexes[event.trackNumber] # in case return is used without call, return to start of track
                    self.players[event.trackNumber] = NotePlayer()
                    self.players[event.trackNumber].play()
                elif isinstance(event, sa.soundSequence.EndTrackSequenceEvent):
                    self.tracks_finished[self.track_current] = True
                    self.event_times_targetDelta[self.track_current] = 0xFFFF
                print(f"({self.event_indexes[self.track_current]}/{len(self.events)-1}) tempo {self.tempo} {event}")
                self.event_indexes[self.track_current] += 1
                if not self.loop and self.event_indexes[self.track_current] > len(self.events)-1:
                    self.stop()
                    return
            #print(f"exec time: {timer()-self.event_time[0]}")
            if not self.next_track(): # if we have gone through all tracks
                wait_time = min(x for x in self.event_times_targetDelta if x > 0)-(timer()-self.event_times[self.track_current])
                print(max(wait_time, 0))
                self.exit_flag.wait(max(wait_time, 0))
            print(f"process next track: {self.track_current}")

    def play(self):
        self.thread = threading.Thread(target=self.callback, daemon=True)
        self.exit_flag = threading.Event()
        self.thread.start()

    def stop(self):
        for player in self.players:
            if player is not None:
                player.stop()
        self.loop = False
        self.tracks_finished = [True]*len(self.tracks_finished)
        print("music stop")