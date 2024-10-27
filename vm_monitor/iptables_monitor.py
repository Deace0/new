import subprocess
import os
import time

class IptablesMonitor:
    def __init__(self, log, log_directory="./logs", snapshot_file="iptables_snapshot.txt", check_interval=60):
        """
        Initialize the IptablesMonitor class.

        Args:
            log (logging.Logger): Logger to use for logging.
            log_directory (str): Directory where logs will be saved.
            snapshot_file (str): File to save the iptables snapshot.
            check_interval (int): Interval in seconds between checks.
        """
        self.logger = log
        self.log_directory = log_directory
        self.snapshot_file = os.path.join(self.log_directory, snapshot_file)
        self.check_interval = check_interval

        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        if not os.path.exists(self.snapshot_file):
            self.logger.info(f"No iptables snapshot found at {self.snapshot_file}. Saving initial snapshot.")
            self.save_initial_iptables_rules()

    def get_current_iptables(self):
        """
        Get the current iptables rules using 'iptables-save'.
        
        Returns:
            str: The current iptables rules as a string.
        """
        try:
            result = subprocess.run(['iptables-save'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                self.logger.error(f"Error executing iptables-save: {result.stderr.decode('utf-8')}")
                return None
            return result.stdout.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error retrieving iptables rules: {str(e)}")
            return None

    def save_initial_iptables_rules(self):
        """
        Save the current iptables rules to the logs directory as the initial snapshot.
        """
        iptables_rules = self.get_current_iptables()
        if iptables_rules:
            try:
                with open(self.snapshot_file, 'w') as f:
                    f.write(iptables_rules)
                self.logger.info(f"Saved initial iptables rules to {self.snapshot_file}.")
            except Exception as e:
                self.logger.error(f"Error saving iptables rules to {self.snapshot_file}: {str(e)}")

    def clean_iptables_rules(self, rules):
        """
        Clean the iptables rules by removing lines that are not relevant for change detection
        such as timestamps or other dynamic data.

        Args:
            rules (str): The iptables rules as a string.

        Returns:
            str: Cleaned iptables rules.
        """
        cleaned_rules = []
        for line in rules.splitlines():
            # Remove lines that start with '#' (comments) or contain dynamic information like timestamps
            if not line.startswith("#"):
                cleaned_rules.append(line)
        return "\n".join(cleaned_rules)

    def compare_iptables(self):
        """
        Compare the current iptables rules with the saved snapshot in the logs directory.

        Returns:
            bool: True if there are changes, False otherwise.
        """
        current_rules = self.get_current_iptables()
        if not current_rules:
            return False

        current_rules_cleaned = self.clean_iptables_rules(current_rules)

        if os.path.exists(self.snapshot_file):
            with open(self.snapshot_file, 'r') as f:
                saved_rules = f.read()

            saved_rules_cleaned = self.clean_iptables_rules(saved_rules)

            if current_rules_cleaned != saved_rules_cleaned:
                self.logger.info("Detected changes in iptables rules.")
                return True
            else:
                self.logger.info("No changes detected in iptables rules.")
                return False
        else:
            self.logger.error(f"{self.snapshot_file} does not exist.")
            return False

    def update_iptables_snapshot(self):
        """
        Update the iptables snapshot in the logs directory with the current rules.
        """
        current_rules = self.get_current_iptables()
        if current_rules:
            try:
                with open(self.snapshot_file, 'w') as f:
                    f.write(current_rules)
                self.logger.info(f"Updated iptables rules in {self.snapshot_file}.")
            except Exception as e:
                self.logger.error(f"Error updating iptables snapshot in {self.snapshot_file}: {str(e)}")

    def monitor_iptables(self):
        """
        Continuously monitor iptables for changes and log if any are detected.
        """
        while True:
            if self.compare_iptables():
                self.logger.warning("iptables rules have changed. Updating snapshot in logs directory.")
                self.update_iptables_snapshot()
            time.sleep(self.check_interval)