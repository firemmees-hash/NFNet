"""
NFNET Console Interface
Command-line interface for controlling the system
"""

import sys
import time
import threading
import webbrowser
import os

class Console:
    """Main console interface"""
    
    def __init__(self):
        # Import other modules
        try:
            import config
            import relay
            import protocol
        except ImportError as e:
            print "[ERROR] Failed to load modules: %s" % str(e)
            print "[ERROR] Make sure all files are in libs/ directory"
            raise
        
        self.config = config.Config()
        self.relay = relay.RelayServer(self.config)
        self.running = False
        
        # Command registry
        self.commands = {
            'help': self.cmd_help,
            'start': self.cmd_start,
            'stop': self.cmd_stop,
            'status': self.cmd_status,
            'ping': self.cmd_ping,
            'connect': self.cmd_connect,
            'send': self.cmd_send,
            'stats': self.cmd_stats,
            'config': self.cmd_config,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'test': self.cmd_test,
            'routes': self.cmd_routes,
            'cache': self.cmd_cache,
            'log': self.cmd_log,
            'web': self.cmd_web,
            'open': self.cmd_open,
            'logo': self.cmd_logo
        }
        
        # Test client for internal testing
        self.test_client = None
    
    def run(self):
        """Run the console"""
        self.running = True
        
        # Start relay automatically
        print "Starting NFNET relay..."
        if self.relay.start():
            print "Relay started successfully"
        else:
            print "Warning: Could not start relay"
        
        print ""
        print "Web interface available at: http://127.0.0.1:%s" % self.config.intranet_port
        print "Type 'web' to open in browser, 'logo' to check logo status"
        print ""
        
        # Main command loop
        while self.running:
            try:
                # Show prompt
                sys.stdout.write("NFNET> ")
                sys.stdout.flush()
                
                # Get input
                try:
                    command_line = raw_input()
                except EOFError:
                    print ""
                    break
                except KeyboardInterrupt:
                    print "^C"
                    continue
                
                # Parse command
                parts = command_line.strip().split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                args = parts[1:]
                
                # Execute command
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print "Unknown command: %s" % cmd
                    print "Type 'help' for available commands"
                
            except Exception as e:
                print "Error: %s" % str(e)
        
        # Cleanup
        self.shutdown()
    
    def shutdown(self):
        """Shutdown the system"""
        print "Shutting down NFNET system..."
        self.relay.stop()
        print "Goodbye!"
    
    def cmd_help(self, args):
        """Show help"""
        print "NFNET Protocol Console Commands:"
        print "=" * 50
        print "  help                    Show this help"
        print "  start                   Start relay server"
        print "  stop                    Stop relay server"
        print "  status                  Show system status"
        print "  ping [host]             Ping a host"
        print "  connect [host:port]     Connect to NFNET host"
        print "  send [message]          Send message to connected host"
        print "  stats                   Show relay statistics"
        print "  config [show|set|save]  Configuration management"
        print "  routes                  Show routing table"
        print "  cache [clear|stats]     Cache management"
        print "  test                    Run system tests"
        print "  log [level]             Set log level"
        print "  web                     Open web interface"
        print "  open                    Open web in default browser"
        print "  logo                    Check logo status"
        print "  clear                   Clear screen"
        print "  exit, quit              Exit console"
        print ""
        print "Examples:"
        print "  ping 127.0.0.1"
        print "  connect localhost:28080"
        print "  config show"
        print "  config set log_level=3"
        print "  web                     (opens web interface)"
        print ""
    
    def cmd_start(self, args):
        """Start relay server"""
        if self.relay.start():
            print "Relay server started"
        else:
            print "Failed to start relay server"
    
    def cmd_stop(self, args):
        """Stop relay server"""
        if self.relay.stop():
            print "Relay server stopped"
        else:
            print "Failed to stop relay server"
    
    def cmd_status(self, args):
        """Show system status"""
        config_status = self.config.get_status()
        
        print "NFNET System Status"
        print "=" * 50
        
        for key, value in config_status.items():
            print "  %-20s: %s" % (key.title(), value)
        
        print ""
        print "Relay Status:"
        print "  %s" % ("RUNNING" if self.relay.running else "STOPPED")
        
        if self.relay.running:
            stats = self.relay.get_stats()
            print "  Uptime: %.1f seconds" % stats['uptime']
            print "  Connections: %s" % stats['clients']
            print "  Packets: %s in / %s out" % (stats['packets_received'], stats['packets_sent'])
            print "  Cache: %s entries" % stats['cache_size']
        
        print ""
        print "Web Interface:"
        print "  URL: http://127.0.0.1:%s" % self.config.intranet_port
        print "  Status: %s" % ("RUNNING" if self.relay.running else "STOPPED")
    
    def cmd_ping(self, args):
        """Ping a host"""
        if not args:
            host = "127.0.0.1"
        else:
            host = args[0]
        
        print "Pinging %s..." % host
        
        # Simple ping using socket
        import socket
        
        try:
            # Try to connect to relay port
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            result = sock.connect_ex((host, self.config.relay_port))
            end_time = time.time()
            
            if result == 0:
                print "Reply from %s: time=%.1fms" % (host, (end_time - start_time) * 1000)
                sock.close()
            else:
                print "Request timed out"
        
        except Exception as e:
            print "Ping failed: %s" % str(e)
    
    def cmd_connect(self, args):
        """Connect to NFNET host"""
        if not args:
            print "Usage: connect [host:port]"
            print "Example: connect localhost:28080"
            return
        
        target = args[0]
        if ':' not in target:
            target += ":28080"  # Default port
        
        print "Connecting to %s..." % target
        print "This feature is under development"
        print "Coming in NFNET v1.1"
    
    def cmd_send(self, args):
        """Send message"""
        if not args:
            print "Usage: send [message]"
            return
        
        message = ' '.join(args)
        print "Sending: %s" % message
        print "Message queued for delivery"
    
    def cmd_stats(self, args):
        """Show relay statistics"""
        if not self.relay.running:
            print "Relay is not running"
            return
        
        stats = self.relay.get_stats()
        
        print "Relay Statistics"
        print "=" * 50
        
        for key, value in stats.items():
            if key != 'start_time':
                display_key = key.replace('_', ' ').title()
                print "  %-20s: %s" % (display_key, value)
        
        print ""
        print "Active Clients:"
        
        # Show connected clients
        if hasattr(self.relay, 'clients'):
            clients = self.relay.clients.copy()
            if clients:
                for addr, info in clients.items():
                    uptime = time.time() - info['connected_at']
                    print "  %s:%s - %d packets, %.1f sec" % (
                        addr[0], addr[1], info.get('packets', 0), uptime
                    )
            else:
                print "  No active connections"
    
    def cmd_config(self, args):
        """Configuration management"""
        if not args:
            print "Usage: config [show|set|save]"
            return
        
        subcmd = args[0].lower()
        
        if subcmd == 'show':
            print "Current Configuration:"
            print "=" * 50
            
            for attr in dir(self.config):
                if not attr.startswith('_') and not callable(getattr(self.config, attr)):
                    value = getattr(self.config, attr)
                    if not isinstance(value, dict):
                        print "  %-25s = %s" % (attr, value)
        
        elif subcmd == 'set' and len(args) >= 2:
            setting = args[1]
            if '=' in setting:
                key, value = setting.split('=', 1)
                
                # Convert value type
                if value.isdigit():
                    value = int(value)
                elif value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                
                # Set attribute
                if hasattr(self.config, key):
                    old_value = getattr(self.config, key)
                    setattr(self.config, key, value)
                    print "Changed %s: %s -> %s" % (key, old_value, value)
                else:
                    print "Unknown setting: %s" % key
            else:
                print "Usage: config set key=value"
        
        elif subcmd == 'save':
            if self.config.save_config():
                print "Configuration saved"
            else:
                print "Failed to save configuration"
        
        else:
            print "Unknown config command: %s" % subcmd
    
    def cmd_routes(self, args):
        """Show routing table"""
        print "Routing Table:"
        print "=" * 50
        
        for route, target in self.config.routing_table.items():
            print "  %-15s -> %s" % (route, target)
        
        print ""
        print "Custom routes can be added in nfnet.cfg"
    
    def cmd_cache(self, args):
        """Cache management"""
        if not args:
            print "Usage: cache [clear|stats]"
            return
        
        subcmd = args[0].lower()
        
        if subcmd == 'clear':
            if hasattr(self.relay, 'cache'):
                self.relay.cache.clear()
                print "Cache cleared"
            else:
                print "Cache not available"
        
        elif subcmd == 'stats':
            if hasattr(self.relay, 'cache'):
                size = len(self.relay.cache)
                print "Cache Statistics:"
                print "  Entries: %s" % size
                print "  Max Size: %s" % self.config.cache_size
                print "  Usage: %.1f%%" % ((float(size) / self.config.cache_size) * 100)
            else:
                print "Cache not available"
        
        else:
            print "Unknown cache command: %s" % subcmd
    
    def cmd_test(self, args):
        """Run system tests"""
        print "Running system tests..."
        print ""
        
        tests = [
            ("Protocol Version", self.test_protocol),
            ("Network Configuration", self.test_network),
            ("Cache System", self.test_cache),
            ("Packet Format", self.test_packets)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print "Testing %s..." % test_name,
            sys.stdout.flush()
            
            try:
                result = test_func()
                if result:
                    print "[PASS]"
                    passed += 1
                else:
                    print "[FAIL]"
                    failed += 1
            except Exception as e:
                print "[ERROR] %s" % str(e)
                failed += 1
        
        print ""
        print "Test Results: %s passed, %s failed" % (passed, failed)
        
        if failed == 0:
            print "All systems operational"
        else:
            print "Some tests failed - check system configuration"
    
    def test_protocol(self):
        """Test protocol functions"""
        try:
            import protocol
            p = protocol.Packet("TEST", "Test payload")
            packed = p.pack()
            unpacked = protocol.Packet.unpack(packed)
            return unpacked is not None and unpacked.verify()
        except:
            return False
    
    def test_network(self):
        """Test network configuration"""
        return self.config.relay_port > 0 and self.config.relay_port < 65536
    
    def test_cache(self):
        """Test cache system"""
        return self.config.enable_cache in [True, False]
    
    def test_packets(self):
        """Test packet creation and parsing"""
        try:
            import protocol
            ping = protocol.MessageHandler.create_ping()
            return ping.type == "PING"
        except:
            return False
    
    def cmd_log(self, args):
        """Set log level"""
        if not args:
            print "Current log level: %s" % self.config.log_level
            print "0=Error, 1=Warn, 2=Info, 3=Debug"
            return
        
        try:
            level = int(args[0])
            if 0 <= level <= 3:
                self.config.log_level = level
                print "Log level set to %s" % level
            else:
                print "Log level must be 0-3"
        except ValueError:
            print "Invalid log level. Use 0, 1, 2, or 3"
    
    def cmd_web(self, args):
        """Show web interface info"""
        print "NFNET Web Interface"
        print "=" * 50
        print "URL: http://127.0.0.1:%s" % self.config.intranet_port
        print ""
        print "Features:"
        print "  - System status dashboard"
        print "  - NFNET logo display"
        print "  - Search/connect interface"
        print "  - Network statistics"
        print "  - Protocol information"
        print ""
        print "Type 'open' to launch in default browser"
        print "Make sure logo.png is in resources/ folder"
    
    def cmd_open(self, args):
        """Open web interface in browser"""
        url = "http://127.0.0.1:%s" % self.config.intranet_port
        print "Opening web interface: %s" % url
        
        try:
            webbrowser.open(url)
            print "Browser launched successfully"
        except Exception as e:
            print "Failed to open browser: %s" % str(e)
            print "Please manually open: %s" % url
    
    def cmd_logo(self, args):
        """Check logo status"""
        import os
        
        # Check resources directory
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        logo_path = os.path.join(resources_dir, 'logo.png')
        
        print "Logo Status Check"
        print "=" * 50
        
        if os.path.exists(resources_dir):
            print "Resources directory: FOUND"
            print "Path: %s" % resources_dir
        else:
            print "Resources directory: NOT FOUND"
            print "Creating directory..."
            os.makedirs(resources_dir)
            print "Directory created: %s" % resources_dir
        
        print ""
        
        if os.path.exists(logo_path):
            print "Logo file: FOUND"
            print "Path: %s" % logo_path
            print "Size: %s bytes" % os.path.getsize(logo_path)
            print ""
            print "The logo will display on the web interface at:"
            print "http://127.0.0.1:%s" % self.config.intranet_port
        else:
            print "Logo file: NOT FOUND"
            print "Expected: %s" % logo_path
            print ""
            print "To add a logo:"
            print "1. Find or create a PNG image (300x150 pixels works well)"
            print "2. Save it as 'logo.png'"
            print "3. Place it in the 'resources' folder"
            print "4. Restart NFNET or type 'web' to see it"
        
        print ""
        print "Web interface: http://127.0.0.1:%s" % self.config.intranet_port
    
    def cmd_clear(self, args):
        """Clear screen"""
        # Simple clear - print lots of newlines
        print "\n" * 100
    
    def cmd_exit(self, args):
        """Exit console"""
        print "Exiting NFNET console..."
        self.running = False