import threading
import time
import json
from vm_monitor import service_monitor, log_utils
from vm_monitor.cpu_monitor import CPUMonitor
from vm_monitor.memory_monitor import MemoryMonitor
from vm_monitor.disk_monitor import DiskMonitor
from vm_monitor.iptables_monitor import IptablesMonitor
from vm_monitor.users_monitor import UsersMonitor  

class Monitor:
    def __init__(self, check_interval=60, config_file="config.json"):
        """
        Initialize the Monitor class.

        Args:
            check_interval (int): The interval in seconds between each check for monitoring.
            config_file (str): Path to the configuration file.
        """
        self.check_interval = check_interval
        self.config = self.load_config(config_file)
        self.logger = log_utils.configure_logging(self.config["log_directory"])
        self.service_monitor = service_monitor.ServiceMonitor(
            log_directory=self.config["log_directory"], 
            check_interval=self.check_interval
        )
        self.iptables_monitor = IptablesMonitor(
            log=self.logger,
            log_directory=self.config["log_directory"],
            check_interval=self.check_interval
        )
        self.users_monitor = UsersMonitor(  
            log=self.logger,
            log_directory=self.config["log_directory"],
            check_interval=self.check_interval
        )

    def load_config(self, config_file):
        """
        Load the configuration from a file.
        """
        with open(config_file, "r") as f:
            return json.load(f)

    def start_cpu_monitor(self):
        while True:
            try:
                cpu_usage = CPUMonitor.get_usage()
                self.logger.info(f"CPU Usage: {cpu_usage}%")
                if cpu_usage > self.config.get("cpu_threshold", 90):
                    self.logger.warning(f"High CPU Usage: {cpu_usage}%")
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error while monitoring CPU: {str(e)}")

    def start_disk_monitor(self):
        while True:
            try:
                disk_usage = DiskMonitor.get_usage()
                self.logger.info(f"Disk Usage: {disk_usage}%")
                if disk_usage > self.config.get("disk_threshold", 90):
                    self.logger.warning(f"High Disk Usage: {disk_usage}%")
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error while monitoring disk: {str(e)}")

    def start_memory_monitor(self):
        while True:
            try:
                memory_usage = MemoryMonitor.get_usage()
                self.logger.info(f"Memory Usage: {memory_usage}%")
                if memory_usage > self.config.get("memory_threshold", 90):
                    self.logger.warning(f"High Memory Usage: {memory_usage}%")
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error while monitoring memory: {str(e)}")

    def start_service_monitor(self):
        self.service_monitor.start_monitoring()

    def start_iptables_monitor(self):
        """
        Start iptables monitoring.
        """
        self.iptables_monitor.monitor_iptables()

    def start_users_monitor(self):
        """
        Start users monitoring.
        """
        self.users_monitor.monitor_users()  

    def start_all_monitors(self):
        threading.Thread(target=self.start_cpu_monitor, daemon=True).start()
        threading.Thread(target=self.start_disk_monitor, daemon=True).start()
        threading.Thread(target=self.start_memory_monitor, daemon=True).start()
        threading.Thread(target=self.start_service_monitor, daemon=True).start()
        threading.Thread(target=self.start_iptables_monitor, daemon=True).start()
        threading.Thread(target=self.start_users_monitor, daemon=True).start() 

if __name__ == "__main__":
    monitor = Monitor(check_interval=60, config_file="config.json")
    monitor.start_all_monitors()

    while True:
        time.sleep(1)
