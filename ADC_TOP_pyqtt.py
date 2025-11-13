import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,QLineEdit
from PyQt5.QtCore import QTimer
import subprocess
import os
import psutil
import time
import fileinput
import json

config_file = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')

def reload_config():
    global config, fs, fb, time_scale, ADC_bits, readfile_offset, readbytes_offset, spectrumfun_sel,dir_path, plot_dir, fft_points, fft_window, plot_real, BYTES_DATA_POINTS, HOST, PORT, TCP_TOTAL, delta, pause_time_fft, pause_time_rt, pause_time_rrt, SIZE_TCPIP_SEND_BUF_TRUNK, TCP_PACKET_CT
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
    BYTES_DATA_POINTS=config['BYTES_DATA_POINTS']
    HOST = config['HOST']
    PORT = config['PORT']
    TCP_TOTAL = config['TCP_TOTAL']
    delta = config['delta']
    pause_time_fft = config['pause_time_fft']
    pause_time_rt = config['pause_time_rt']
    pause_time_rrt = config['pause_time_rrt']
    SIZE_TCPIP_SEND_BUF_TRUNK = config['SIZE_TCPIP_SEND_BUF_TRUNK']
    TCP_PACKET_CT = config['TCP_PACKET_CT']
reload_config()
class GUIApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADC_TOP     Author : QianLei")

        self.receive_data_button = QPushButton("接收数据", self)
        self.receive_data_button.clicked.connect(self.execute_receive_data_script)

        self.stop_receive_data_button = QPushButton("停止接收数据", self)
        self.stop_receive_data_button.clicked.connect(self.execute_stop_receive_data_script)

        self.plot_button = QPushButton("画图", self)
        self.plot_button.clicked.connect(self.execute_plot_script)

        self.spectrum_button = QPushButton("画频谱图", self)
        self.spectrum_button.clicked.connect(self.execute_spectrum_script)

        self.realtime_plot_button = QPushButton("实时画图", self)
        self.realtime_plot_button.clicked.connect(self.execute_realtime_plot_script)

        self.realtime_spectrum_button = QPushButton("实时频谱图", self)
        self.realtime_spectrum_button.clicked.connect(self.execute_realtime_spectrum_script)

        self.plotmaxsndr_button = QPushButton("画最大SNDR图", self)
        self.plotmaxsndr_button.clicked.connect(self.execute_plotmaxsndr_script)

        self.savedata_button = QPushButton("保存单次数据", self)
        self.savedata_button.clicked.connect(self.execute_savedata_script)

        self.write_config_button = QPushButton("写入配置", self)
        self.write_config_button.clicked.connect(self.write_config)

        self.receive_data_process = None
        self.script_directory = os.path.dirname(os.path.realpath(__file__))

        self.network_speed_label = QLabel("当前网速: N/A", self)

        self.monitor_network_speed_timer = QTimer(self)
        self.monitor_network_speed_timer.timeout.connect(self.update_network_speed)
        self.monitor_network_speed_timer.start(1000)

        self.fs_label = QLabel("fs:", self)
        self.fs_textbox = QLineEdit(self)
        self.fs_textbox.setText(str(fs))
        self.fs_textbox.setPlaceholderText("输入 fs 值")

        self.fb_label = QLabel("fb:", self)
        self.fb_textbox = QLineEdit(self)
        self.fb_textbox.setText(str(fb))
        self.fb_textbox.setPlaceholderText("输入 fb 值")

        self.time_scale_label = QLabel("time_scale:", self)
        self.time_scale_textbox = QLineEdit(self)
        self.time_scale_textbox.setText(str(time_scale))
        self.time_scale_textbox.setPlaceholderText("输入 time_scale 值")

        self.adc_bits_label = QLabel("ADC_bits:", self)
        self.adc_bits_textbox = QLineEdit(self)
        self.adc_bits_textbox.setText(str(ADC_bits))
        self.adc_bits_textbox.setPlaceholderText("输入 ADC_bits 值")

        self.readfile_offset_label = QLabel("readfile_offset:", self)
        self.readfile_offset_textbox = QLineEdit(self)
        self.readfile_offset_textbox.setText(str(readfile_offset))
        self.readfile_offset_textbox.setPlaceholderText("输入 readfile_offset 值")

        self.readbytes_offset_label = QLabel("readbytes_offset:", self)
        self.readbytes_offset_textbox = QLineEdit(self)
        self.readbytes_offset_textbox.setText(str(readbytes_offset))
        self.readbytes_offset_textbox.setPlaceholderText("输入 readbytes_offset 值")

        self.spectrumfun_sel_label = QLabel("spectrumfun_sel:", self)
        self.spectrumfun_sel_textbox = QLineEdit(self)
        self.spectrumfun_sel_textbox.setText(str(spectrumfun_sel))
        self.spectrumfun_sel_textbox.setPlaceholderText("输入 spectrumfun_sel 值")

        self.dir_path_label = QLabel("dir_path:", self)
        self.dir_path_textbox = QLineEdit(self)
        self.dir_path_textbox.setText(str(dir_path))
        self.dir_path_textbox.setPlaceholderText("输入 dir_path 值")

        self.plot_dir_label = QLabel("plot_dir:", self)
        self.plot_dir_textbox = QLineEdit(self)
        self.plot_dir_textbox.setText(str(plot_dir))
        self.plot_dir_textbox.setPlaceholderText("输入 plot_dir 值")

        self.fft_points_label = QLabel("fft_points:", self)
        self.fft_points_textbox = QLineEdit(self)
        self.fft_points_textbox.setText(str(fft_points))
        self.fft_points_textbox.setPlaceholderText("输入 fft_points 值")

        self.fft_window_label = QLabel("fft_window:", self)
        self.fft_window_textbox = QLineEdit(self)
        self.fft_window_textbox.setText(str(fft_window))
        self.fft_window_textbox.setPlaceholderText("输入 fft_window 值")

        self.plot_real_label = QLabel("plot_real:", self)
        self.plot_real_textbox = QLineEdit(self)
        self.plot_real_textbox.setText(str(plot_real))
        self.plot_real_textbox.setPlaceholderText("输入 plot_real 值")
        self.timer = QTimer(self)
        # 将定时器的timeout信号连接到更新网速的槽函数
        self.timer.timeout.connect(self.update_network_speed)
        # 设置定时器间隔为1秒
        self.timer.start(1000)  # 1000毫秒 = 1秒   
        self.last_bytes = 0     


        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.receive_data_button)
        layout.addWidget(self.stop_receive_data_button)
        layout.addWidget(self.plot_button)
        layout.addWidget(self.spectrum_button)
        layout.addWidget(self.realtime_plot_button)
        layout.addWidget(self.realtime_spectrum_button)
        layout.addWidget(self.plotmaxsndr_button)
        layout.addWidget(self.savedata_button)
        layout.addWidget(self.write_config_button)
        layout.addWidget(self.network_speed_label)
        layout.addWidget(self.fs_label)
        layout.addWidget(self.fs_textbox)
        layout.addWidget(self.fb_label)
        layout.addWidget(self.fb_textbox)
        layout.addWidget(self.time_scale_label)
        layout.addWidget(self.time_scale_textbox)
        layout.addWidget(self.adc_bits_label)
        layout.addWidget(self.adc_bits_textbox)
        layout.addWidget(self.readfile_offset_label)
        layout.addWidget(self.readfile_offset_textbox)
        layout.addWidget(self.readbytes_offset_label)
        layout.addWidget(self.readbytes_offset_textbox)
        layout.addWidget(self.spectrumfun_sel_label)
        layout.addWidget(self.spectrumfun_sel_textbox)
        layout.addWidget(self.dir_path_label)
        layout.addWidget(self.dir_path_textbox)
        layout.addWidget(self.plot_dir_label)
        layout.addWidget(self.plot_dir_textbox)
        layout.addWidget(self.fft_points_label)
        layout.addWidget(self.fft_points_textbox)
        layout.addWidget(self.fft_window_label)
        layout.addWidget(self.fft_window_textbox)
        layout.addWidget(self.plot_real_label)
        layout.addWidget(self.plot_real_textbox)
        self.setLayout(layout)
        self.resize(600, 800)  # Adjust the width and height as needed

    def execute_receive_data_script(self):
        script_path1 = os.path.join(self.script_directory, "tcp_recv_ADC.py")
        self.receive_data_process = subprocess.Popen(["python", script_path1])

    def execute_stop_receive_data_script(self):
        if self.receive_data_process:
            self.receive_data_process.terminate()
            self.receive_data_process = None

    def execute_plot_script(self):
        script_path2 = os.path.join(self.script_directory, "plot_wave_single.py")
        subprocess.Popen(["python", script_path2])

    def execute_spectrum_script(self):
        script_path3 = os.path.join(self.script_directory, "plot_spectrum_single.py")
        subprocess.Popen(["python", script_path3])

    def execute_realtime_plot_script(self):
        script_path4 = os.path.join(self.script_directory, "plot_wave_RRT.py")
        subprocess.Popen(["python", script_path4])

    def execute_realtime_spectrum_script(self):
        script_path5 = os.path.join(self.script_directory, "plot_spectrum_RT.py")
        subprocess.Popen(["python", script_path5])

    def execute_plotmaxsndr_script(self):
        script_path6 = os.path.join(self.script_directory, "plot_max_sndr.py")
        subprocess.Popen(["python", script_path6])
    
    def execute_savedata_script(self):
        script_path7 = os.path.join(self.script_directory, "savedata.py")
        subprocess.Popen(["python", script_path7])

    def write_config(self):
        global fs, fb, time_scale, ADC_bits, readfile_offset, readbytes_offset,spectrumfun_sel, dir_path, plot_dir, fft_points, fft_window, plot_real, BYTES_DATA_POINTS, HOST, PORT, TCP_TOTAL, delta, pause_time_fft, pause_time_rt, pause_time_rrt, SIZE_TCPIP_SEND_BUF_TRUNK, TCP_PACKET_CT
        fs = int(self.fs_textbox.text())
        fb = int(self.fb_textbox.text())
        time_scale = int(self.time_scale_textbox.text())
        ADC_bits = int(self.adc_bits_textbox.text())
        readfile_offset = int(self.readfile_offset_textbox.text())
        readbytes_offset = int(self.readbytes_offset_textbox.text())
        spectrumfun_sel = int(self.spectrumfun_sel_textbox.text())
        dir_path = self.dir_path_textbox.text()
        plot_dir = self.plot_dir_textbox.text()
        fft_points = int(self.fft_points_textbox.text())
        fft_window = self.fft_window_textbox.text()
        plot_real = int(self.plot_real_textbox.text())

        config_data = {
            "fs": fs,
            "fb": fb,
            "time_scale": time_scale,
            "ADC_bits": ADC_bits,
            "readfile_offset": readfile_offset,
            "readbytes_offset": readbytes_offset,
            "spectrumfun_sel": spectrumfun_sel,
            "dir_path": dir_path,
            "plot_dir": plot_dir,
            "fft_points": fft_points,
            "fft_window": fft_window,
            "plot_real": plot_real,
            "BYTES_DATA_POINTS": BYTES_DATA_POINTS,
            "HOST": HOST,
            "PORT": PORT,
            "TCP_TOTAL": TCP_TOTAL,
            "delta": delta,
            "pause_time_fft": pause_time_fft,
            "pause_time_rt": pause_time_rt,
            "pause_time_rrt": pause_time_rrt,
            "SIZE_TCPIP_SEND_BUF_TRUNK": SIZE_TCPIP_SEND_BUF_TRUNK,
            "TCP_PACKET_CT": TCP_PACKET_CT
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)

        # 更新全局配置
        reload_config()
        

    def update_network_speed(self):
        try:
            wifi_interface = '以太网 5'  # 修改为你系统中对应的WiFi接口名称
            bytes_recv = psutil.net_io_counters(pernic=True)[wifi_interface].bytes_recv
            # 计算网速
            net_speed = (bytes_recv - self.last_bytes) / 1024  # 换算为 KB
            self.last_bytes = bytes_recv
            # 更新网速后立即重新启动定时器
            self.timer.start(1000)  # 1000毫秒 = 1秒
            self.network_speed_label.setText(f"当前网速({wifi_interface}): {net_speed:.2f} KB/s")
        except Exception as e:
            print(f"Error monitoring network speed: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUIApp()
    window.show()
    sys.exit(app.exec_())
