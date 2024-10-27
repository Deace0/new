import subprocess
import os
import time

class UsersMonitor:
    def __init__(self, log, log_directory="./logs", snapshot_file="users_snapshot.txt", check_interval=60):
        """
        Initialize the UsersMonitor class.

        Args:
            log (logging.Logger): Logger to use for logging.
            log_directory (str): Directory where logs will be saved.
            snapshot_file (str): File to save the users snapshot.
            check_interval (int): Interval in seconds between checks.
        """
        self.logger = log
        self.log_directory = log_directory
        self.snapshot_file = os.path.join(self.log_directory, snapshot_file)
        self.check_interval = check_interval

        # Ensure the log directory exists
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # Save the initial snapshot of users and permissions if it doesn't exist
        if not os.path.exists(self.snapshot_file):
            self.logger.info(f"No users snapshot found at {self.snapshot_file}. Saving initial snapshot.")
            self.save_initial_users_snapshot()

    def get_current_users(self):
        """
        Get the current list of users and their permissions using 'getent passwd'.
        
        Returns:
            str: The current users and their information as a string.
        """
        try:
            result = subprocess.run(['getent', 'passwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                self.logger.error(f"Error executing getent passwd: {result.stderr.decode('utf-8')}")
                return None
            return result.stdout.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error retrieving users information: {str(e)}")
            return None

    def save_initial_users_snapshot(self):
        """
        Save the current list of users and their permissions to the logs directory as the initial snapshot.
        """
        users_info = self.get_current_users()
        if users_info:
            try:
                with open(self.snapshot_file, 'w') as f:
                    f.write(users_info)
                self.logger.info(f"Saved initial users snapshot to {self.snapshot_file}.")
            except Exception as e:
                self.logger.error(f"Error saving users snapshot to {self.snapshot_file}: {str(e)}")

    def compare_users(self):
        """
        Compare the current users and permissions with the saved snapshot in the logs directory.

        Returns:
            bool: True if there are changes, False otherwise.
        """
        current_users = self.get_current_users()
        if not current_users:
            return False

        # Load the saved users snapshot from the logs directory
        if os.path.exists(self.snapshot_file):
            with open(self.snapshot_file, 'r') as f:
                saved_users = f.read()

            if current_users != saved_users:
                self.logger.info("Detected changes in users or their permissions.")
                return True
            else:
                self.logger.info("No changes detected in users or their permissions.")
                return False
        else:
            self.logger.error(f"{self.snapshot_file} does not exist.")
            return False

    def update_users_snapshot(self):
        """
        Update the users snapshot in the logs directory with the current users information.
        """
        current_users = self.get_current_users()
        if current_users:
            try:
                with open(self.snapshot_file, 'w') as f:
                    f.write(current_users)
                self.logger.info(f"Updated users snapshot in {self.snapshot_file}.")
            except Exception as e:
                self.logger.error(f"Error updating users snapshot in {self.snapshot_file}: {str(e)}")

    def monitor_users(self):
        """
        Continuously monitor users for changes and log if any are detected.
        """
        while True:
            if self.compare_users():
                self.logger.warning("Users or their permissions have changed. Updating snapshot in logs directory.")
                self.update_users_snapshot()
            time.sleep(self.check_interval)
