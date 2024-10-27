import psutil
import logging


class CPUMonitor:
    @staticmethod
    def get_usage(interval=1):
        """
        Returns the current CPU usage as a percentage.
        Handles exceptions if CPU usage cannot be retrieved.
        """
        try:
            return psutil.cpu_percent(interval=interval)
        except Exception as e:
            logging.error(f"Failed to get CPU usage: {e}")
            return None
