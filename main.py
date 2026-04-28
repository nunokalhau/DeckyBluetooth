import subprocess
import re
import logging

# Setup logging
logger = logging.getLogger("Bluetooth")
logger.setLevel(logging.DEBUG)

class Plugin:
    def __init__(self):
        self.logger = logger

    async def _main(self):
        """Initialize plugin with health checks"""
        try:
            # Check if bluetoothctl is available
            result = subprocess.run(
                ["which", "bluetoothctl"],
                timeout=5,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.logger.error("bluetoothctl not found in system PATH")
                return
            self.logger.info("Bluetooth plugin initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin: {str(e)}")

    async def _unload(self):
        """Cleanup on plugin unload"""
        self.logger.info("Bluetooth plugin unloaded")

    async def _call_bluetoothctl(self, args, timeout=10):
        """
        Safely call bluetoothctl with error handling.
        Returns tuple: (success: bool, output: str, error: str)
        """
        try:
            result = subprocess.run(
                ["bluetoothctl"] + args,
                timeout=timeout,
                text=True,
                capture_output=True
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                self.logger.warning(f"bluetoothctl {' '.join(args)} failed: {error_msg}")
                return False, "", error_msg
            
            return True, result.stdout, ""
        except subprocess.TimeoutExpired:
            error_msg = f"bluetoothctl command timed out after {timeout}s"
            self.logger.error(error_msg)
            return False, "", error_msg
        except FileNotFoundError:
            error_msg = "bluetoothctl binary not found"
            self.logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return False, "", error_msg

    async def get_bluetooth_status(self):
        """Get current bluetooth status"""
        success, output, error = await self._call_bluetoothctl(["show"])
        if not success:
            self.logger.error(f"Failed to get bluetooth status: {error}")
            return f"Error: {error}"
        return output

    async def get_paired_devices(self):
        """Get list of paired bluetooth devices"""
        try:
            # Get bluetoothctl version
            success, version_output, error = await self._call_bluetoothctl(["version"])
            
            if not success:
                self.logger.warning(f"Could not determine bluetoothctl version: {error}, trying fallback")
                # Fallback to older command
                success, devices, error = await self._call_bluetoothctl(["paired-devices"])
                if not success:
                    return f"Error: Could not retrieve paired devices: {error}"
                return devices
            
            # Parse version safely
            bctl_version = re.findall(r'\d+', version_output)
            
            if len(bctl_version) >= 2:
                major = int(bctl_version[0])
                minor = int(bctl_version[1])
                
                # Use newer command if version >= 5.66
                if major > 5 or (major == 5 and minor >= 66):
                    success, devices, error = await self._call_bluetoothctl(["devices", "Paired"])
                else:
                    success, devices, error = await self._call_bluetoothctl(["paired-devices"])
            else:
                # Fallback if version parsing fails
                success, devices, error = await self._call_bluetoothctl(["paired-devices"])
            
            if not success:
                return f"Error: {error}"
            
            return devices
        except Exception as e:
            error_msg = f"Error retrieving paired devices: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def get_device_info(self, device):
        """Get information about a specific device"""
        try:
            if not device or not isinstance(device, str):
                return "Error: Invalid device parameter"
            
            success, output, error = await self._call_bluetoothctl(["info", device])
            if not success:
                return f"Error: Could not retrieve device info: {error}"
            return output
        except Exception as e:
            error_msg = f"Error retrieving device info: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def toggle_device_connection(self, device, connected):
        """Connect or disconnect a bluetooth device"""
        try:
            if not device or not isinstance(device, str):
                return "Error: Invalid device parameter"
            
            command = "disconnect" if connected else "connect"
            success, output, error = await self._call_bluetoothctl([command, device])
            
            if not success:
                return f"Error: Failed to {command} device: {error}"
            return output
        except Exception as e:
            error_msg = f"Error toggling device connection: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def toggle_bluetooth(self, state):
        """Toggle bluetooth power on/off"""
        try:
            if not state or not isinstance(state, str):
                return "Error: Invalid state parameter"
            
            if state.lower() not in ["on", "off"]:
                return f"Error: Invalid state '{state}'. Use 'on' or 'off'"
            
            success, output, error = await self._call_bluetoothctl(["power", state.lower()])
            
            if not success:
                return f"Error: Failed to set power: {error}"
            return output
        except Exception as e:
            error_msg = f"Error toggling bluetooth: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
