import time
import binascii
import sys
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
from datetime import datetime
from fun_cal_sndr import cal_sndr
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
############################################  DEFINE END   ########################################
fin_bin = 417
def process_data(data):
    values = np.zeros(len(data)//BYTES_DATA_POINTS)
    for i in range(0, len(data), BYTES_DATA_POINTS):
        values[i//BYTES_DATA_POINTS] = int.from_bytes(data[i:i+BYTES_DATA_POINTS], byteorder='little')
    return values
def data_generator(chunk_data_size):
    while True:
        data=bytearray()
        with open(str_file_read, "rb") as file:
            file.seek(pos)
            data=file.read(chunk_data_size)
            if (len(data)<chunk_data_size):
                on_close
        chunk_data = process_data(data)
        yield chunk_data  # 返回数据     
def on_close(event):
    sys.exit()          
pos=readbytes_offset           
# 创建一个生成器对象
data_gen = data_generator(chunk_data_size)
# 创建Matplotlib图形
fig,ax=plt.subplots() 
fig.canvas.mpl_connect('close_event', on_close)
times=0
max_values = {'fin': float('-inf'), 'sndr': float('-inf'), 'irn_pow': float('inf'), 'irn': float('inf'), 'enob': float('-inf'), 'thd_odd': float('-inf'), 'thd_even': float('-inf'), 'thd': float('-inf'), 'snr': float('-inf'), 'sfdr': float('-inf'), 'Fom': float('-inf')}
# 创建时间起点
time_init=time.time()
try:
    for data_chunk in data_gen:
        times+=1
        data_chunk=np.array(data_chunk)/2**(ADC_bits)*1.8
        sndr,enob,irn,fin,fft_data,fft_freq,irn_pow,thd_odd,thd_even,thd,snr,sfdr= cal_sndr(data_chunk[1:fft_points+1],fs,fb,fin_bin,fft_window)
        ax.clear()
        plt.title("Specrum of the signal")
        plt.xlabel('Frequency/Hz')
        plt.ylabel('AMPLITUDE(dBFS)')
        plt.xlim(1,fs/2)
        plt.ylim(-160,0)
        Fom=sndr+10*np.log10(fb/22e-6)
        max_values['fin'] = max(max_values['fin'], fin)
        max_values['sndr'] = max(max_values['sndr'], sndr)
        max_values['irn_pow'] = min(max_values['irn_pow'], irn_pow)
        max_values['irn'] = min(max_values['irn'], irn)
        max_values['enob'] = max(max_values['enob'], enob)
        max_values['thd_odd'] = max(max_values['thd_odd'], thd_odd) 
        max_values['thd_even'] = max(max_values['thd_even'], thd_even)
        max_values['thd'] = max(max_values['thd'], thd)
        max_values['snr'] = max(max_values['snr'], snr)
        max_values['sfdr'] = max(max_values['sfdr'], sfdr)
        max_values['Fom'] = max(max_values['Fom'], Fom)
        text_content = (f'Freq:  {fin:.2f}Hz \n'
                        f'SNDR:  {sndr:.2f}dB (Max: {max_values["sndr"]:.2f}dB)\n'
                        f'IRN_P: {irn_pow:.2f} (Min: {max_values["irn_pow"]:.2f})\n'
                        f'IRN:   {irn:.9f} (Min: {max_values["irn"]:.9f})\n'
                        f'ENOB:  {round(enob, 2)}bit (Max: {max_values["enob"]:.2f}bit)\n'
                        f'THD@35:{thd_odd:.2f}dB (Max: {max_values["thd_odd"]:.2f}dB)\n'
                        f'THD@24:{thd_even:.2f}dB (Max: {max_values["thd_even"]:.2f}dB)\n'
                        f'THD:   {thd:.2f}dB (Max: {max_values["thd"]:.2f}dB)\n'
                        f'SNR:   {snr:.2f}dB (Max: {max_values["snr"]:.2f}dB)\n'
                        f'SFDR:  {sfdr:.2f}dB (Max: {max_values["sfdr"]:.2f}dB)\n'
                        f'FOM:   {Fom:.2f}dB (Max: {max_values["Fom"]:.2f}dB)')
        text_box = AnchoredText(text_content, loc='upper left', prop=dict(size=8))
        text_box.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        ax.add_artist(text_box)
        xdata=fft_freq
        ydata=10*np.log10(fft_data)
        line, = plt.semilogx(xdata, ydata)
        line.set_data(xdata, ydata)
        plt.draw()
        plt.pause(pause_time_fft)
        pos += chunk_data_size
        if (times==15):
            print(f"程序执行时间：{time.time()-time_init}秒")
except (KeyboardInterrupt):
    plt.close('all')


