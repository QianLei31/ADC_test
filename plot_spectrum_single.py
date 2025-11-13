import socket
import binascii
from matplotlib.offsetbox import AnchoredText
import matplotlib.pyplot as plt
import os
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import AutoLocator, AutoMinorLocator
from scipy.ndimage import gaussian_filter
from matplotlib.colorbar import Colorbar
from collections import deque
from fun_cal_sndr import cal_sndr
from fun_cal_snr import cal_snr
from test_fftclean import fft_clean
import sys
import json
############################################  USER DEFINE  ###################################
config_file = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
with open(config_file, 'r') as f:
    config = json.load(f)
fs = config['fs']
fb = config['fb']
time_scale = config['time_scale']
ADC_bits = config['ADC_bits']
readfile_offset = config['readfile_offset']
readbytes_offset = config['readbytes_offset']
spectrumfun_sel=config['spectrumfun_sel']
dir_path = config['dir_path']
plot_dir = config['plot_dir']
fft_points = config['fft_points']
fft_window = config['fft_window']
plot_real = config['plot_real']
BYTES_DATA_POINTS =config['BYTES_DATA_POINTS']
HOST = config['HOST']
PORT = config['PORT']
TCP_TOTAL = config['TCP_TOTAL']
delta = config['delta']
pause_time_fft = config['pause_time_fft']
pause_time_rt = config['pause_time_rt']
pause_time_rrt = config['pause_time_rrt']
SIZE_TCPIP_SEND_BUF_TRUNK = config['SIZE_TCPIP_SEND_BUF_TRUNK']
TCP_PACKET_CT = config['TCP_PACKET_CT']
Count_max = TCP_TOTAL//TCP_PACKET_CT
chunk_data_size = int(fs * 4 * delta)
axis_range = chunk_data_size//2
axis_range_rrt = axis_range//time_scale
subdirectories = [os.path.join(dir_path, d) for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
subdirectories.sort(key=lambda x: os.path.getctime(x), reverse=True)
readdir = subdirectories[readfile_offset]
if plot_real == 0:
    plotdir = os.path.join(dir_path, plot_dir)
else:
    plotdir = readdir
strPathRead = plotdir
str_file_read = os.path.join(strPathRead, "ADC_DATA.bin")
################################################################################################
def process_data(data):
    values = np.zeros(len(data)//BYTES_DATA_POINTS)
    for i in range(0, len(data), BYTES_DATA_POINTS):
        values[i//BYTES_DATA_POINTS] = int.from_bytes(data[i:i+BYTES_DATA_POINTS], byteorder='little')
    return values
with open(str_file_read, "rb") as file:
    file.seek(readbytes_offset)
    data=file.read(fft_points*4)
data=process_data(data)/2**ADC_bits*1.8
##################cal_sndr##################
fin_bin=417
if (spectrumfun_sel==1):
    sndr,enob,irn,fin,fft_data,fft_freq,irn_pow,thd_odd,thd_even,thd,snr,sfdr= cal_sndr(data,fs,fb,fin_bin,fft_window)

    fig,ax=plt.subplots() 
    plt.title("Specrum of the signal")
    plt.xlabel('Frequency/Hz')
    plt.ylabel('AMPLITUDE(dBFS)')
    text_content = f'Freq: {fin:.2f}Hz\nSNDR: {sndr:.2f}dB\nIRN_POWER:{irn_pow:.2f}\nIRN:{irn:.9f}\nENOB: {round(enob,2)}bit'
    text_box = AnchoredText(text_content, loc='upper right')
    text_box.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(text_box)
    xdata=fft_freq
    ydata=10*np.log10(fft_data)
    line, = plt.semilogx(xdata, ydata)
    line.set_data(xdata, ydata)
    plt.show()
elif (spectrumfun_sel==2):
    snr,spectP = cal_snr(data,fb,fs,title='test',log=1)
    plt.show()
else :
    fft_freq, fft_data, sndr, enob, signband_power, sig_power,dc_power = fft_clean(data, fs, 1, 123.5, 4)
    print(sndr, enob, signband_power, sig_power,dc_power)
    fig,ax=plt.subplots() 
    plt.title("Specrum of the signal")
    plt.xlabel('Frequency/Hz')
    plt.ylabel('AMPLITUDE(dBFS)')
    text_content = f'SNDR: {sndr:.2f}dB\nENOB: {round(enob,2)}bit'
    text_box = AnchoredText(text_content, loc='upper right')
    text_box.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(text_box)
    xdata=fft_freq
    ydata=10*np.log10(fft_data)
    line, = plt.semilogx(xdata, ydata)
    line.set_data(xdata, ydata)
    plt.show()


