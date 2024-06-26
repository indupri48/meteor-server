from rtlsdr import RtlSdr
import numpy as np
from PIL import Image
import scipy.signal as signal

print("")
print("##############")
print("# RTL Meteor #")
print("#  by M7JDK  #")
print("##############")
print("")

waterfall_length = 64 * 16
fft_length = 1024
sample_rate = 2.4e6

trigger_snr = 0

bandwidth = 400_000

waterfall = np.zeros((waterfall_length, fft_length), dtype=np.uint8)

sdr = RtlSdr()
sdr.center_freq = 103.7e6
sdr.sample_rate = sample_rate
sdr.gain = 'auto'
sdr.freq_correction = 60

print("Starting...")

count = 0
while True:

    samples = sdr.read_samples(fft_length)
    samples = signal.decimate(samples, int(sample_rate / bandwidth))

    fft_result = np.fft.fftshift(np.fft.fft(samples, n=fft_length))
    power_spectrum = np.abs(fft_result) ** 2
    #power_spectrum = 10.0 * np.log10(power_spectrum)
    
    if count > 0:

        count += 1

        if count == fft_length / 2:
            print("Capture saved!")
            im = Image.fromarray(waterfall)
            im.save("waterfall.png", "PNG")
            count = 0

    else:

        if np.max(power_spectrum) > np.median(power_spectrum) + trigger_snr:
            print("Triggered!")
            count = 1

    waterfall = np.roll(waterfall, 1, axis=0)

    power_spectrum_range = np.max(power_spectrum) - np.min(power_spectrum)
    waterfall_line = ((power_spectrum - np.min(power_spectrum)) * 255) / power_spectrum_range
    waterfall[0] = np.astype(waterfall_line, np.uint8)

