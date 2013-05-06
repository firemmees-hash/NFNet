"""
NFNET Configuration Module
Handles all system settings and preferences
"""
# -*- coding: utf-8 -*-
import os

class Config:
    """Configuration management for NFNET"""
    
    def __init__(self):
        # Core protocol settings
        self.protocol_name = "NFNET"
        self.protocol_version = "1.0"
        self.build_number = 143
        
        # Network configuration
        self.listen_ip = "0.0.0.0"  # Listen on all interfaces
        self.relay_port = 28080      # Main relay port
        self.control_port = 28081    # Control channel
        self.intranet_port = 8080    # Local web interface
        
        # Performance settings
        self.max_clients = 50
        self.buffer_size = 8192      # 8KB buffers
        self.timeout = 45            # Connection timeout in seconds
        self.keep_alive = True
        
        # Feature flags
        self.enable_cache = True
        self.cache_size = 500        # Max cache entries
        self.enable_compression = False  # Coming in v1.1
        self.enable_ssl = False      # SSL support experimental
        
        # Debug settings
        self.log_level = 2           # 0=Error, 1=Warn, 2=Info, 3=Debug
        self.log_file = "nfnet.log"
        
        # Custom routing
        self.routing_table = {
            "intranet": "127.0.0.1:8080",
            "api": "127.0.0.1:28081",
            "relay": "127.0.0.1:28080"
        }
        
        # Load custom config if exists
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if present"""
        config_file = "nfnet.cfg"
        if os.path.exists(config_file):
            try:
                print "[CONFIG] Loading settings from %s" % config_file
                # Simple config parser
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Convert types
                                if value.isdigit():
                                    value = int(value)
                                elif value.lower() == 'true':
                                    value = True
                                elif value.lower() == 'false':
                                    value = False
                                
                                # Set attribute if it exists
                                if hasattr(self, key):
                                    setattr(self, key, value)
                                    print "[CONFIG] Set %s = %s" % (key, value)
            except Exception as e:
                print "[CONFIG ERROR] %s" % str(e)
    
    def save_config(self):
        """Save current settings to file"""
        config_file = "nfnet.cfg"
        try:
            with open(config_file, 'w') as f:
                f.write("# NFNET Configuration File\n")
                f.write("# Generated automatically\n\n")
                
                # Write all attributes
                for attr in dir(self):
                    if not attr.startswith('_') and not callable(getattr(self, attr)):
                        value = getattr(self, attr)
                        if not isinstance(value, dict):
                            f.write("%s = %s\n" % (attr, value))
                
            print "[CONFIG] Settings saved to %s" % config_file
            return True
        except Exception as e:
            print "[CONFIG ERROR] Could not save: %s" % str(e)
            return False
    
    def get_status(self):
        """Return current configuration status"""
        return {
            'protocol': "%s v%s" % (self.protocol_name, self.protocol_version),
            'build': self.build_number,
            'network': "Listening on %s:%s" % (self.listen_ip, self.relay_port),
            'clients': "Max %s concurrent" % self.max_clients,
            'cache': "Enabled (%s entries)" % self.cache_size if self.enable_cache else "Disabled",
            'compression': "Enabled" if self.enable_compression else "Disabled",
            'ssl': "Enabled" if self.enable_ssl else "Disabled"
        }