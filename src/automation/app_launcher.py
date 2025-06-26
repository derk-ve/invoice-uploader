import os
import subprocess
from .base_automation import BaseAutomation


class AppLauncher(BaseAutomation):
    """Handles launching the Snelstart application."""
    
    def _get_app_path(self):
        """Get the configured Snelstart application path."""
        return self.config.get('snelstart', {}).get('app_path', '')
    
    def _validate_app_path(self, app_path):
        """Validate that the application path exists and is configured."""
        if not app_path:
            self.logger.error("Snelstart application path not configured")
            return False
        
        if not os.path.exists(app_path):
            self.logger.error(f"Snelstart executable not found at: {app_path}")
            return False
        
        return True
    
    def _launch_from_wsl(self, app_path):
        """Launch Snelstart from WSL environment using cmd.exe."""
        self.logger.info("Detected WSL environment - using cmd.exe to launch")
        subprocess.Popen(['cmd.exe', '/c', 'start', '""', app_path], shell=False)
    
    def _launch_from_windows(self, app_path):
        """Launch Snelstart directly from Windows environment."""
        self.logger.info("Detected Windows environment - launching directly")
        subprocess.Popen([app_path])
    
    def _execute_launch(self, app_path):
        """Execute the platform-specific launch command."""
        if self.is_wsl:
            self._launch_from_wsl(app_path)
        else:
            self._launch_from_windows(app_path)
    
    def _wait_for_startup(self):
        """Wait for the application to start up."""
        self.logger.info("Waiting for Snelstart to start...")
        self.wait(5)  # Give the app time to launch
    
    def launch_snelstart(self):
        """Launch Snelstart application."""
        app_path = self._get_app_path()
        
        if not self._validate_app_path(app_path):
            return False
        
        self.logger.info(f"Launching Snelstart from: {app_path}")
        
        try:
            self._execute_launch(app_path)
            self._wait_for_startup()
            
            self.logger.info("Snelstart launched successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch Snelstart: {str(e)}")
            return False