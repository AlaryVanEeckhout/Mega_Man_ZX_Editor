import sounddevice, numpy

class WAVPlayer:
    def __init__(self, data: numpy.ndarray, samplerate: int, loop: int|None, totalLen):
        self.data = data # 1d array
        assert len(data.shape) == 1
        self.loop = loop
        self.current_frame = 0
        self.totalLen = totalLen
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
        print(len(self.data), self.totalLen)
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
