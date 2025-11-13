import socket
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import time
import math
import sys
import json
##########################################  USER DEFINE  ###################################
config_file = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
with open(config_file, 'r') as f:
    config = json.load(f)
fs = config['fs']
fb = config['fb']
time_scale = config['time_scale']
ADC_bits = config['ADC_bits']
readfile_offset = config['readfile_offset']
readbytes_offset = config['readbytes_offset']
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
###########################################  DEFINE END   ########################################
dir=dir_path
save=1
# 获取当前时间
current_time = datetime.now() 
month = current_time.month
day = current_time.day
hour = current_time.hour
minute = current_time.minute
savedir = os.path.join(dir, f'{month:02d}{day:02d}_{hour:02d}{minute:02d}')
os.makedirs(savedir, exist_ok=True)
bty_file_write= savedir+  "/"+ "ADC_DATA"+".bin"
def recieve_tcpip (conn,num_to_recieve,max_attemp=-1):
    cnt_attemp=0
    data=bytearray()
    while ((num_to_recieve >0) and (cnt_attemp<=max_attemp or max_attemp==-1)):
        rx_data = []
        cnt_attemp = cnt_attemp + 1
        rx_data = conn.recv(min(num_to_recieve,SIZE_TCPIP_SEND_BUF_TRUNK))
        data.extend(rx_data) 
        len_recv_data=len(rx_data)   
        num_to_recieve=num_to_recieve-len_recv_data
    return data
def process_data(data):
    values = np.zeros(len(data)//BYTES_DATA_POINTS)
    for i in range(0, len(data), BYTES_DATA_POINTS):
        values[i//BYTES_DATA_POINTS] = int.from_bytes(data[i:i+BYTES_DATA_POINTS], byteorder='little')
    return values

if save==1:
    # 定义目标文件夹路径
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        message = "ctread"
        s.sendall(message.encode())
        cnt_ctread=0
        with open(bty_file_write,"ab+") as h_file_results:
            h_file_results.seek(0)
            h_file_results.truncate()
            while cnt_ctread<Count_max:
                recv_data =recieve_tcpip(s,TCP_PACKET_CT)
                h_file_results.write(recv_data)
                cnt_ctread += 1
        print(f"Received finish\n")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 关闭连接
        s.close()
    print("TCP传输完成")