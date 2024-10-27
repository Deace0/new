import psutil
import logging


class DiskMonitor:
    @staticmethod
    def get_usage(path="/"):
        """
        Returns the current disk usage as a percentage.
        Handles exceptions if disk usage cannot be retrieved.
        """
        try:
            disk_info = psutil.disk_usage(path)
            return disk_info.percent
        except Exception as e:
            logging.error(f"Failed to get disk usage: {e}")
            return None
