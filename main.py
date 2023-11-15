import platform
import subprocess
import psutil
import wmi
import GPUtil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def get_system_info():
    cpu_info = get_cpu_info()

    gpus = GPUtil.getGPUs()
    gpu_info = "GPU:"
    for i, gpu in enumerate(gpus, 1):
        gpu_info += f"\n  {i}. {gpu.name}"

    motherboard_info = get_motherboard_info()

    ram_info = get_ram_info()

    storage_info = get_storage_info()

    network_info = get_network_info()

    system_info = f"{cpu_info}\n\n{gpu_info}\n\n{motherboard_info}\n\n{ram_info}\n\n{storage_info}\n\n{network_info}"

    return system_info

def get_cpu_info():
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()['brand_raw']
        return f"CPU: {info}"
    except ImportError:
        system_info = platform.uname()
        return f"CPU: {system_info.processor}"
    except Exception as e:
        print(f"Error retrieving CPU information: {e}")
        return "CPU information not available"

def get_motherboard_info():
    try:
        c = wmi.WMI()
        for board in c.Win32_BaseBoard():
            return f"Motherboard: {board.Product}"
        return "Motherboard information not available"
    except Exception as e:
        print(f"Error retrieving motherboard information: {e}")
        return "Motherboard information not available"

def get_ram_info():
    try:
        ram_info = "RAM:"
        if platform.system().lower() == 'windows':
            wmi_info = get_ram_info_wmi()
            if wmi_info:
                ram_info += wmi_info
            else:
                ram_info += "\n  RAM information not available on this system."
        else:
            ram_info += "\n  RAM information not available on this system."
        return ram_info
    except Exception as e:
        print(f"Error retrieving RAM information: {e}")
        return "RAM information not available"

def get_ram_info_wmi():
    try:
        c = wmi.WMI()
        ram_info = ""
        for i, ram in enumerate(c.Win32_PhysicalMemory(), 1):
            try:
                model = ram.PartNumber.strip()
                capacity_gb = int(ram.Capacity) / (1024 ** 3)
                ram_info += f"\n  {i}. {model} - {capacity_gb:.2f} GB"
            except (ValueError, TypeError):
                print(f"Error parsing RAM capacity for {ram.Tag}. Skipping.")
        return ram_info
    except Exception as e:
        print(f"Error retrieving RAM information using WMI: {e}")
        return None

def get_storage_info():
    try:
        partitions = psutil.disk_partitions()
        storage_info = "Storage:"
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            storage_info += f"\n  {partition.device} - {partition.fstype} " \
                            f"({usage.total / (1024 ** 3):.2f} GB total, {usage.free / (1024 ** 3):.2f} GB free)"
        return storage_info
    except Exception as e:
        print(f"Error retrieving storage information: {e}")
        return "Storage information not available"

def get_network_info():
    try:
        network_info = "Network:"
        if psutil.net_if_stats():
            for interface, stats in psutil.net_if_stats().items():
                network_info += f"\n  {interface}: {'WiFi' if 'Wi-Fi' in stats else 'Ethernet'}"
        else:
            network_info += "\n  No network information available."
        return network_info
    except Exception as e:
        print(f"Error retrieving network information: {e}")
        return "Network information not available"

class SystemInfoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PCP")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        system_info_text = QTextEdit(self)
        system_info_text.setPlainText(get_system_info())
        system_info_text.setReadOnly(True)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(45, 0, 70))
        palette.setColor(QPalette.WindowText, Qt.white)

        system_info_text.setPalette(palette)

        layout.addWidget(system_info_text)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    system_info_app = SystemInfoApp()
    system_info_app.show()
    app.exec_()

    # Add the following lines to make the script wait for Enter before closing
    print("\nPress Enter to exit...")
    input()
