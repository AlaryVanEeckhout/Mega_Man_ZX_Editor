try:
    import sounddevice
except OSError:
    print("PortAudio library not found")
    raise ImportError # trigger the except block from sdat instead of actually crashing
import numpy
import ndspy.soundArchive as sa
from timeit import default_timer as timer
import sched
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

class SSEQScheduler:
    def __init__(self, callback):
        self.callback = callback
        self.thread = None
        self.exit_flag = None
        self.sched = None
    
    def thread_fn(self):
        self.sched = sched.scheduler(timer, self.exit_flag.wait)
        self.sched.enter(0, 0, self.callback)
        # gives control to scheduler until all events are run
        self.sched.run()

    def add_event(self, time, action, *args):
        #print(f"{time}: {action}")
        self.sched.enterabs(time, 0, action, args)

    def start(self):
        self.thread = threading.Thread(target=self.thread_fn, daemon=True)
        self.exit_flag = threading.Event()
        self.thread.start()
    
    def stop(self):
        # todo
        pass

class Track:
    def __init__(self, event_index=0):
        self.sample_index: int = 0 # index into bank instruments
        self.event_index: int = event_index
        self.event_time_last: int = 0 # time of next event
        self.event_time_targetDelta: int = 0 # target waiting time
        self.return_index: int = event_index # in case return is used without call, return to start of track
        self.loop_index: int = 0 # used with begin and end loop events
        self.loop_count: int = 0 # used with begin and end loop events
        self.player: NotePlayer = NotePlayer()
        self.player.play()

class SSEQPlayer:
    def __init__(self, events: list[sa.soundSequence.SequenceEvent], sample_list:list[Sample], loop: int=None):
        self.events = events
        self.sample_list = sample_list
        self.loop = loop # should this exist?
        self.tempo = 150
        self.TRACKS_MAX = 16 # IDs 0 to 15
        self.tracks: list[Track] = [None]*self.TRACKS_MAX
        self.time_start = 0 # used to set event_time_last of tracks
        self.scheduler = SSEQScheduler(lambda: self.process_events_of_track(0))


    def get_bpm_tick(self):
        return BPM_TICK_FACTOR / self.tempo


    def play(self):
        self.time_start = timer()
        # the first track will start the others
        self.tracks[0] = Track()
        self.tracks[0].event_time_last = self.time_start
        self.scheduler.start()

    def process_events_of_track(self, track_current: int):
        track = self.tracks[track_current]
        print(f"track: {track_current}")
        if track.player.stream.active == False:
            raise InterruptedError
        while track.event_time_targetDelta == 0:
            event = self.events[track.event_index]
            sample = self.sample_list[track.sample_index]
            if isinstance(event, sa.soundSequence.NoteSequenceEvent):
                if sample is not None:
                    duration = int(self.get_bpm_tick()*event.duration*track.player.stream.samplerate) # for sample array
                    sample_selected = sample
                    if isinstance(sample, list):
                        sample_selected = sample[event.pitch]
                    if sample_selected is not None:
                        print(f"samplerate {sample_selected.samplerate}")
                        track.player.play_note(event, sample_selected, duration)
            elif isinstance(event, sa.soundSequence.RestSequenceEvent):
                # not actually a musical rest, how long to stop parsing events and let music play
                # only this instruction sets event_time_targetDelta
                track.event_time_targetDelta = self.get_bpm_tick()*event.duration
                print(f"tdelta {track.event_time_targetDelta}")
            elif isinstance(event, sa.soundSequence.InstrumentSwitchSequenceEvent):
                track.sample_index = event.instrumentID
            elif isinstance(event, sa.soundSequence.TempoSequenceEvent):
                self.tempo = event.value
            elif isinstance(event, sa.soundSequence.CallSequenceEvent):
                track.return_index = track.event_index
                track.event_index = next((i for i, obj in enumerate(self.events) if obj is event.destination))
            elif isinstance(event, sa.soundSequence.JumpSequenceEvent):
                track.event_index = next((i for i, obj in enumerate(self.events) if obj is event.destination))
            elif isinstance(event, sa.soundSequence.ReturnSequenceEvent):
                track.event_index = track.return_index
            elif isinstance(event, sa.soundSequence.EndLoopSequenceEvent):
                pass # todo
            elif isinstance(event, sa.soundSequence.BeginLoopSequenceEvent):
                track.loop_index = track.event_index
                # wip
            elif isinstance(event, sa.soundSequence.BeginTrackSequenceEvent): # For Tracks other than Track 0
                self.tracks[event.trackNumber] = Track(next((i for i, obj in enumerate(self.events) if obj is event.firstEvent)))
                self.tracks[event.trackNumber].event_time_last = self.time_start
                self.scheduler.add_event(0, self.process_events_of_track, event.trackNumber) # start chain of events for this track
            elif isinstance(event, sa.soundSequence.EndTrackSequenceEvent):
                print("end")
                return
            print(f"({track.event_index}/{len(self.events)-1}) tempo {self.tempo} {event}")
            track.event_index += 1
            if not self.loop and track.event_index > len(self.events)-1:
                self.stop()
                return
        track.event_time_last += track.event_time_targetDelta
        track.event_time_targetDelta = 0
        self.scheduler.add_event(track.event_time_last, self.process_events_of_track, track_current)


    def stop(self):
        for track in self.tracks:
            if track is not None:
                track.player.stop()
        self.scheduler.stop()
        print("music stop")