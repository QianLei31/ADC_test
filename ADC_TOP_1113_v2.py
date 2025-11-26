import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit
from PyQt5.QtCore import QTimer
import subprocess
import os
import psutil
import json

# ---------------------- 全局配置 ----------------------
config_file = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')

# 全局变量，将在 reload_config 中填充
config = {}
fs = 0
fb = 0
time_scale = 0
ADC_bits = 0
readfile_offset = 0
readbytes_offset = 0
spectrumfun_sel = 0
dir_path = ""
plot_dir = ""
fft_points = 0
fft_window = ""
plot_real = 0
BYTES_DATA_POINTS = 0
HOST = ""
PORT = 0
TCP_TOTAL = 0
delta = 0
pause_time_fft = 0
pause_time_rt = 0
pause_time_rrt = 0
SIZE_TCPIP_SEND_BUF_TRUNK = 0
TCP_PACKET_CT = 0


def reload_config():
    """从 config.json 重新加载全局配置变量"""
    global config, fs, fb, time_scale, ADC_bits, readfile_offset, readbytes_offset
    global spectrumfun_sel, dir_path, plot_dir, fft_points, fft_window, plot_real
    global BYTES_DATA_POINTS, HOST, PORT, TCP_TOTAL, delta
    global pause_time_fft, pause_time_rt, pause_time_rrt
    global SIZE_TCPIP_SEND_BUF_TRUNK, TCP_PACKET_CT

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        # 使用 .get() 提供默认值，防止 config 文件中缺项导致崩溃
        fs = config.get('fs', 1000)
        fb = config.get('fb', 100)
        time_scale = config.get('time_scale', 1)
        ADC_bits = config.get('ADC_bits', 16)
        readfile_offset = config.get('readfile_offset', 0)
        readbytes_offset = config.get('readbytes_offset', 0)
        spectrumfun_sel = config.get('spectrumfun_sel', 0)
        dir_path = config.get('dir_path', '.')
        plot_dir = config.get('plot_dir', '.')
        fft_points = config.get('fft_points', 1024)
        fft_window = config.get('fft_window', 'hanning')
        plot_real = config.get('plot_real', 0)
        BYTES_DATA_POINTS = config.get('BYTES_DATA_POINTS', 2)
        HOST = config.get('HOST', '127.0.0.1')
        PORT = config.get('PORT', 8080)
        TCP_TOTAL = config.get('TCP_TOTAL', 1024)
        delta = config.get('delta', 1)
        pause_time_fft = config.get('pause_time_fft', 0.1)
        pause_time_rt = config.get('pause_time_rt', 0.1)
        pause_time_rrt = config.get('pause_time_rrt', 0.1)
        SIZE_TCPIP_SEND_BUF_TRUNK = config.get('SIZE_TCPIP_SEND_BUF_TRUNK', 4096)
        TCP_PACKET_CT = config.get('TCP_PACKET_CT', 1)

    except FileNotFoundError:
        print(f"❌ 配置文件 {config_file} 未找到。将使用默认值。")
    except json.JSONDecodeError:
        print(f"❌ 配置文件 {config_file} 格式错误。将使用默认值。")
    except Exception as e:
        print(f"❌ 加载配置时出错: {e}")


# 启动时加载一次配置
reload_config()


# ---------------------- GUI 主类 ----------------------
class GUIApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADC_TOP     Author : QianLei")
        self.script_directory = os.path.dirname(os.path.realpath(__file__))
        self.receive_data_process = None
        self.last_bytes = 0

        # ---------------- 按钮区 ----------------
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

        # ---------------- 网络监控 ----------------
        self.network_speed_label = QLabel("当前网速: N/A", self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_network_speed)
        self.timer.start(1000)  # 每秒更新一次

        # ---------------- 配置参数输入 ----------------
        self.fs_label = QLabel("fs:")
        self.fs_textbox = QLineEdit(str(fs))

        self.fb_label = QLabel("fb:")
        self.fb_textbox = QLineEdit(str(fb))

        self.time_scale_label = QLabel("time_scale:")
        self.time_scale_textbox = QLineEdit(str(time_scale))

        self.adc_bits_label = QLabel("ADC_bits:")
        self.adc_bits_textbox = QLineEdit(str(ADC_bits))

        self.readfile_offset_label = QLabel("readfile_offset:")
        self.readfile_offset_textbox = QLineEdit(str(readfile_offset))

        self.readbytes_offset_label = QLabel("readbytes_offset:")
        self.readbytes_offset_textbox = QLineEdit(str(readbytes_offset))

        self.spectrumfun_sel_label = QLabel("spectrumfun_sel:")
        self.spectrumfun_sel_textbox = QLineEdit(str(spectrumfun_sel))

        self.dir_path_label = QLabel("dir_path:")
        self.dir_path_textbox = QLineEdit(str(dir_path))

        self.plot_dir_label = QLabel("plot_dir:")
        self.plot_dir_textbox = QLineEdit(str(plot_dir))

        self.fft_points_label = QLabel("fft_points:")
        self.fft_points_textbox = QLineEdit(str(fft_points))

        self.fft_window_label = QLabel("fft_window:")
        self.fft_window_textbox = QLineEdit(str(fft_window))

        self.plot_real_label = QLabel("plot_real (1=自动, 0=手动):")
        self.plot_real_textbox = QLineEdit(str(plot_real))

        # ---------------- 布局 ----------------
        layout = QVBoxLayout()
        for widget in [
            self.receive_data_button,
            self.stop_receive_data_button,
            self.plot_button,
            self.spectrum_button,
            self.realtime_plot_button,
            self.realtime_spectrum_button,
            self.plotmaxsndr_button,
            self.savedata_button,
            self.write_config_button,
            self.network_speed_label,
            self.fs_label, self.fs_textbox,
            self.fb_label, self.fb_textbox,
            self.time_scale_label, self.time_scale_textbox,
            self.adc_bits_label, self.adc_bits_textbox,
            self.readfile_offset_label, self.readfile_offset_textbox,
            self.readbytes_offset_label, self.readbytes_offset_textbox,
            self.spectrumfun_sel_label, self.spectrumfun_sel_textbox,
            self.dir_path_label, self.dir_path_textbox,
            self.plot_dir_label, self.plot_dir_textbox,
            self.fft_points_label, self.fft_points_textbox,
            self.fft_window_label, self.fft_window_textbox,
            self.plot_real_label, self.plot_real_textbox
        ]:
            layout.addWidget(widget)

        self.setLayout(layout)
        self.resize(600, 800)

        # 根据初始 plot_real 值设置 UI
        self.update_ui_for_plot_real()

    # ---------------- 核心逻辑：自动/手动执行 ----------------
    def run_with_auto_receive(self, script_name):
        """
        根据全局变量 plot_real (在写入配置时更新)
        - 1: 自动启动接收数据，画图窗口关闭时自动停止
        - 0: 只启动画图，不自动启停接收
        """
        script_path = os.path.join(self.script_directory, script_name)

        if plot_real == 1:
            # --- 自动模式 ---
            recv_script = os.path.join(self.script_directory, "tcp_recv_ADC.py")
            print(f"📡 (自动模式) 启动接收数据：{recv_script}")
            
            # 确保之前的进程已关闭
            if self.receive_data_process:
                self.receive_data_process.terminate()
                self.receive_data_process = None

            self.receive_data_process = subprocess.Popen(["python", recv_script])

            print(f"🖌️ (自动模式) 启动画图脚本：{script_path}")
            # 执行画图脚本（阻塞等待）
            try:
                plot_proc = subprocess.Popen(["python", script_path])
                plot_proc.wait()  # 等待画图脚本结束 (即窗口关闭)
            finally:
                # 自动停止接收数据
                if self.receive_data_process:
                    print("🛑 (自动模式) 画图窗口关闭，自动关闭接收数据进程")
                    self.receive_data_process.terminate()
                    self.receive_data_process = None
        else:
            # --- 手动模式 ---
            print(f"🖌️ (手动模式) 启动画图脚本：{script_path}")
            print("    (请确保已手动点击 '接收数据')")
            subprocess.Popen(["python", script_path])

    # ---------------- 脚本执行函数 (手动) ----------------
    def execute_receive_data_script(self):
        if self.receive_data_process:
            print("⚠️ 接收进程已在运行")
            return
        script_path = os.path.join(self.script_directory, "tcp_recv_ADC.py")
        print(f"📡 (手动模式) 启动接收数据：{script_path}")
        self.receive_data_process = subprocess.Popen(["python", script_path])

    def execute_stop_receive_data_script(self):
        if self.receive_data_process:
            print("🛑 (手动模式) 关闭接收数据进程")
            self.receive_data_process.terminate()
            self.receive_data_process = None
        else:
            print("ℹ️ 接收进程未运行")

    # ---------------- 画图按钮槽函数 ----------------
    def execute_plot_script(self):
        self.run_with_auto_receive("plot_wave_single.py")

    def execute_spectrum_script(self):
        self.run_with_auto_receive("plot_spectrum_single.py")

    def execute_realtime_plot_script(self):
        self.run_with_auto_receive("plot_wave_RRT.py")

    def execute_realtime_spectrum_script(self):
        self.run_with_auto_receive("plot_spectrum_RT.py")

    def execute_plotmaxsndr_script(self):
        self.run_with_auto_receive("plot_max_sndr.py")

    def execute_savedata_script(self):
        script_path = os.path.join(self.script_directory, "savedata.py")
        subprocess.Popen(["python", script_path])

    # ---------------- 写入配置 ----------------
    def write_config(self):
        global fs, fb, time_scale, ADC_bits, readfile_offset, readbytes_offset
        global spectrumfun_sel, dir_path, plot_dir, fft_points, fft_window, plot_real

        try:
            # 从文本框读取值
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

            # 更新配置字典
            config_data = config.copy() # 继承其他未显示的配置
            config_data.update({
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
                "plot_real": plot_real
            })

            # 写入文件
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            # 关键：重新加载全局变量
            reload_config() 
            
            # 关键：根据新配置更新 UI 状态
            self.update_ui_for_plot_real()
            
            print("✅ 配置已写入并重新加载")
            
        except ValueError as e:
            print(f"❌ 写入配置失败：请输入有效的数字。错误：{e}")
        except Exception as e:
            print(f"❌ 写入配置失败：{e}")

    # ---------------- UI 更新 ----------------
    def update_ui_for_plot_real(self):
        """根据 plot_real 的值更新 UI 状态，使其不那么“麻烦”"""
        
        # 确保我们读取的是当前文本框中的值
        try:
            current_plot_real = int(self.plot_real_textbox.text())
        except ValueError:
            current_plot_real = plot_real # 如果文本框无效，使用已加载的全局变量
            
        is_auto_mode = (current_plot_real == 1)
        
        # 禁用/启用手动按钮
        self.receive_data_button.setEnabled(not is_auto_mode)
        self.stop_receive_data_button.setEnabled(not is_auto_mode)
        
        # 更新按钮文本以反映模式
        if is_auto_mode:
            self.receive_data_button.setText("接收数据 (自动模式)")
            self.stop_receive_data_button.setText("停止接收 (自动模式)")
        else:
            self.receive_data_button.setText("接收数据")
            self.stop_receive_data_button.setText("停止接收数据")

    # ---------------- 网速更新 ----------------
    def update_network_speed(self):
        try:
            # 尝试找到一个活动的以太网或 Wi-Fi 接口
            net_io = psutil.net_io_counters(pernic=True)
            target_interface = None
            
            # 常见的接口名称关键字
            common_interfaces = ['Ethernet', '以太网', 'Wi-Fi', 'WLAN']
            
            for interface_name in net_io:
                for common_name in common_interfaces:
                    if common_name in interface_name:
                        target_interface = interface_name
                        break
                if target_interface:
                    break
            
            # 如果找不到，就使用 '以太网 5' 作为后备 (用户的原始设置)
            if not target_interface and '以太网 5' in net_io:
                target_interface = '以太网 5' 

            if target_interface and target_interface in net_io:
                bytes_recv = net_io[target_interface].bytes_recv
                net_speed = (bytes_recv - self.last_bytes) / 1024
                self.last_bytes = bytes_recv
                self.network_speed_label.setText(f"当前网速({target_interface}): {net_speed:.2f} KB/s")
            else:
                self.network_speed_label.setText(f"当前网速: 未找到接口")

        except Exception as e:
            # print(f"Error monitoring network speed: {e}")
            self.network_speed_label.setText("当前网速: 错误")


# ---------------------- 主程序入口 ----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUIApp()
    window.show()
    sys.exit(app.exec_())