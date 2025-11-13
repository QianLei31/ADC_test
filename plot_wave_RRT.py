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
spectrumfun_sel = config['spectrumfun_sel']
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
def data_generator(chunk_data_size):
    while True:
        data=bytearray()
        with open(str_file_read, "rb") as file:
            file.seek(current_pos)
            data=file.read(chunk_data_size)
            if (len(data)<chunk_data_size):
                on_close
        chunk_data = process_data(data)
        yield chunk_data  # 返回数据     
def on_close(event):
    sys.exit()                   
# 创建一个生成器对象
current_pos=readbytes_offset
data_gen = data_generator(chunk_data_size//time_scale)
# 创建Matplotlib图形
fig=plt.figure()
plt.title("ADC Data Reconfigured Real Time")
plt.xlabel("Time")
plt.ylabel("Voltage")
fig.canvas.mpl_connect('close_event', on_close)
xdata = deque(maxlen=axis_range_rrt//2)
ydata = deque(maxlen=axis_range_rrt//2)
line, = plt.plot(xdata, ydata)
# 设置初始的 x 轴和 y 轴范围
plt.xlim(0, axis_range_rrt/fs)  # 设置 x 轴范围
plt.ylim(0, 1.8)  # 设置 y 轴范围
cnt_shift = 0
times=0
time_init=time.time()
try:
    for data_chunk in data_gen:
        times+=1
        time_sample=np.arange(cnt_shift*chunk_data_size//4/fs,cnt_shift*chunk_data_size//4/fs+len(data_chunk)/fs,1/fs)
        xdata.extend(time_sample)
        data_chunk=[x/2**(ADC_bits)*1.8 for x in data_chunk]
        ydata.extend(data_chunk)
        line.set_data(xdata, ydata)
        current_pos += chunk_data_size
        plt.xlim(min(xdata),max(xdata))  # 动态设置 x 轴范围
        plt.draw()
        plt.pause(pause_time_rrt)  # 间隔时间，以控制数据更新速度
        if (times==15):
            print(f"程序执行时间：{time.time()-time_init}秒")
        cnt_shift += 1  # 
except (KeyboardInterrupt):
    plt.close('all')


