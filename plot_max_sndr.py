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
import sys
import json
import csv
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
max_enob = 0
deltafft=fft_points
best_index_sndr = -1
def process_data(data):
    values = np.zeros(len(data)//BYTES_DATA_POINTS)
    for i in range(0, len(data), BYTES_DATA_POINTS):
        values[i//BYTES_DATA_POINTS] = int.from_bytes(data[i:i+BYTES_DATA_POINTS], byteorder='little')
    return values
with open(str_file_read, "rb") as file:
    file.seek(readbytes_offset)
    data_b=file.read()
    if len(data_b)<fft_points*4:
        print('file too short')
        exit()
data=np.array(process_data(data_b))/2**(ADC_bits)*1.8

##################cal_sndr##################
fin_bin=417
for i in range(0, len(data) - fft_points + 1, deltafft):  # 每次增加 delta
    segment = data[i:i + fft_points]
    sndr,enob,irn,fin,fft_data,fft_freq,irn_pow,thd_odd,thd_even,thd,snr,sfdr= cal_sndr(segment,fs,fb,fin_bin,fft_window)
    if enob > max_enob:
        max_enob = enob
        best_index_sndr = i
print(best_index_sndr,'best_index')

if best_index_sndr != -1:
    max_enob_segment = data[best_index_sndr:best_index_sndr + fft_points]
    max_enob_file_path = strPathRead + '/maxenob.csv'
    with open(max_enob_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for value in max_enob_segment:
            csvwriter.writerow([value])
    print('max_enob_segment saved to:', max_enob_file_path)

sndr,enob,irn,fin,fft_data,fft_freq,irn_pow,thd_odd,thd_even,thd,snr,sfdr= cal_sndr(data[best_index_sndr:best_index_sndr + fft_points],fs,fb,fin_bin,fft_window)
fig, ax = plt.subplots(figsize=(22,8))
plt.xlim(10,fs/2)
plt.ylim(-180,0)
# 设置坐标轴标签字体
plt.xlabel('Frequency/Hz', fontsize=24, fontname='Times New Roman', fontweight='bold')
plt.ylabel('Amplitude(dBFS)', fontsize=24, fontname='Times New Roman', fontweight='bold')

# 设置刻度标签字体
plt.xticks(fontsize=25, fontname='Times New Roman', fontweight='bold')
plt.yticks(fontsize=25, fontname='Times New Roman', fontweight='bold')

# 设置边框加粗
spine_len=4
ax.spines['top'].set_linewidth(spine_len)
ax.spines['right'].set_linewidth(spine_len)
ax.spines['bottom'].set_linewidth(spine_len)
ax.spines['left'].set_linewidth(spine_len)
# 设置刻度线加粗
ax.tick_params(axis='both', width=4)

# 设置网格线为虚线
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
text_content = f'Freq = {fin:.2f}Hz\nSNR = {snr:.2f}dB\nSNDR = {sndr:.2f}dB\nTHD = {thd:.2f}dB\nSFDR = {sfdr:.2f}dB'
text_box = AnchoredText(text_content, loc='upper left', prop=dict(size=30, fontname='Times New Roman', weight='bold'))
text_box.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
text_box.patch.set_linewidth(2)  # 设置边框加粗
ax.add_artist(text_box)
xdata=fft_freq
ydata=10*np.log10(fft_data)
line, = plt.semilogx(xdata, ydata, 'b')  # 设置曲线颜色为蓝色
line.set_data(xdata, ydata)
fb_bin=fb/(fs/fft_points)
plt.axvline(x=fb, color='r', linestyle='--')
plt.text(0.95, 0.95, f"{fft_points} points FFT", horizontalalignment='right', verticalalignment='top', fontsize=30, fontname='Times New Roman',  fontweight='bold',fontstyle='italic', transform=ax.transAxes)
plt.text(0.95, 0.87, f"Window='{fft_window}'", horizontalalignment='right', verticalalignment='top', fontsize=30, fontname='Times New Roman', fontweight='bold',fontstyle='italic', transform=ax.transAxes)

# 在 x=2000, y=-140 的位置画一条红色线段
plt.plot([20000, 60000], [-140, -140], color='red', linewidth=3)
# 在 x=6000, y=-140 的位置画一条红色线段
plt.plot([60000, 60000], [-140, -105], color='red', linewidth=3)
# 在 x=6000, y=-110 的位置画一条红色线段
plt.plot([60000, 20000], [-105, -140], color='red', linewidth=3)
plt.text(30000, -150, '60dB/dec', color='red', fontsize=25, fontname='Times New Roman', fontweight='bold')

plt.show()


