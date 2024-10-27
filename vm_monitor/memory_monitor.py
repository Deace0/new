import psutil
import logging


class MemoryMonitor:
    @staticmethod
    def get_usage():
        """
        Returns the current memory usage as a percentage.
        Handles exceptions if memory usage cannot be retrieved.
        """
        try:
            memory_info = psutil.virtual_memory()
            return memory_info.percent
        except Exception as e:
            logging.error(f"Failed to get memory usage: {e}")
            return None
