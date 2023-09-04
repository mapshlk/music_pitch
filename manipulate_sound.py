import numpy as np
from pydub import AudioSegment
from scipy.io.wavfile import write, read
from matplotlib import pyplot as plt
import pyaudio
import wave

def change_pitch(file, factor):
    # Step 1, sampling
    raw = AudioSegment.from_mp3(file)
    raw.export("temp.wav", format="wav")
    rate, data = read("temp.wav")
    new_data = data.copy()

    if False:        
        # Step 2, changing the pitch
        data = np.array(data, dtype=np.float64)
        fft_data = np.fft.rfft(data)
        fft_shifted = np.roll(fft_data, int(len(fft_data)*factor))
        new_data = np.fft.irfft(fft_shifted).astype(np.int16)
    
    # iterate over the data array and identify changes from negative to positive values
    print(data.shape)
    prev = data[0,1]
    wave_count = 0
    i0 = 0
    amplitude_sample_rate = 8
    double_frequency = False
    for i in range(1, len(data)):
        if prev < 0 and data[i,1] > 0:
            if wave_count < amplitude_sample_rate:
                wave_count += 1
            else:
                wave_count = 0
                print(f"start: {i0}, len: {i-i0}, prev {prev}")
                if double_frequency:
                    for j in range(i-i0):
                        new_index = i0 + 2*j
                        if new_index > i:
                            new_index = new_index - (i-i0)
                        new_data[i0+j,0] = data[new_index,0]
                        new_data[i0+j,1] = data[new_index,1]
                        #print(new_index, i0+j, new_data[i0+j], data[i0+j])
                else:
                    for j in range(i-i0):
                        if j%2 == 0:
                            data_value = data[i0 + j//2,:]
                        else:
                            data_value = (data[i0 + j//2,:] + data[i0 + j//2 + 1,:]) // 2
                        new_data[i0+j] = data_value
                i0 = i
        prev = data[i,1]

    plt.plot(data)
    plt.plot(new_data)
    plt.show()
        
    # Step 3, writing the manipulated data
    write("temp_pitch_changed.wav", rate, new_data)
        
    # Step 4, playing the manipulated sampled data 
    CHUNK = 1024  # number of data points to read at a time
    wf = wave.open("temp_pitch_changed.wav", 'rb')

    p = pyaudio.PyAudio()  # instantiate PyAudio 

    # open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True)
    data = wf.readframes(CHUNK) 

    # play stream 
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # stop stream 
    stream.stop_stream()
    stream.close()

    # close PyAudio 
    p.terminate()

# Example usage
change_pitch('nause-03.mp3', 0.5)
