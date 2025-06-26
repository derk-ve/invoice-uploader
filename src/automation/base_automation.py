import pyautogui
import platform
import time


class EnvironmentDetector:
    """Detects the current operating environment."""
    
    @staticmethod
    def is_wsl():
        """Check if running in WSL environment."""
        return 'microsoft' in platform.uname().release.lower()


class BaseAutomation:
    """Base class for all automation components."""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.delay = config.get('automation', {}).get('delay', 2.0)
        self.is_wsl = EnvironmentDetector.is_wsl()
        
        # Set pyautogui settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.delay
    
    def wait(self, seconds=None):
        """Wait for specified time or default delay."""
        wait_time = seconds if seconds is not None else self.delay
        time.sleep(wait_time)