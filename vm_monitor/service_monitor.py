import os
import time
import threading
import subprocess
import log_utils

class ServiceMonitor:
    def __init__(self, log_directory="./logs", whitelist_file='service_whitelist.txt', check_interval=60):
        """
        Initialize the ServiceMonitor class.

        Args:
            log_directory (str): Directory where logs will be saved.
            whitelist_file (str): Name of the whitelist file.
            check_interval (int): Interval in seconds between checks.
        """
        self.log_directory = log_directory
        self.logger = log_utils.configure_logging(self.log_directory)  # הגדר את ה-logger כאן לפני כל השאר
        self.whitelist_file = os.path.join(self.log_directory, whitelist_file)
        self.check_interval = check_interval
        self.whitelisted_services = self.load_whitelist()

    def load_whitelist(self):
        if not os.path.exists(self.whitelist_file):
            self.logger.warning(f"Whitelist file {self.whitelist_file} does not exist. Creating a new one.")
            with open(self.whitelist_file, 'w') as f:
                f.write('')

        with open(self.whitelist_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def get_active_services(self):
        try:
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running'], stdout=subprocess.PIPE)
            services = result.stdout.decode('utf-8').splitlines()
            active_services = [line.split()[0] for line in services if '.service' in line]
            return active_services
        except Exception as e:
            self.logger.error(f"Error retrieving active services: {str(e)}")
            return []

    def monitor_services(self):
        while True:
            try:
                active_services = self.get_active_services()
                for service in active_services:
                    if service not in self.whitelisted_services:
                        self.logger.info(f"New service detected: {service}")
                        self.whitelisted_services.append(service)
                        self.update_whitelist_file(service)

                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error while monitoring services: {str(e)}")

    def update_whitelist_file(self, service):
        with open(self.whitelist_file, 'a') as f:
            f.write(f"{service}\n")
        self.logger.info(f"Service {service} added to whitelist.")

    def start_monitoring(self):
        monitor_thread = threading.Thread(target=self.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
