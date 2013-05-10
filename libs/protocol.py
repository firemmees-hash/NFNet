"""
NFNET Protocol Implementation
Custom protocol for network communication
"""

class Packet:
    """Base packet structure for NFNET protocol"""
    
    def __init__(self, packet_type="DATA", payload="", options=None):
        self.version = 1
        self.type = packet_type  # DATA, CONTROL, PING, ROUTE, ERROR
        self.id = self._generate_id()
        self.timestamp = self._get_timestamp()
        self.payload = payload
        self.options = options or {}
        self.checksum = 0
    
    def _generate_id(self):
        """Generate a packet ID"""
        import random
        return random.randint(1000, 9999)
    
    def _get_timestamp(self):
        """Get current timestamp"""
        import time
        return int(time.time())
    
    def calculate_checksum(self):
        """Calculate simple checksum for integrity"""
        data = str(self.type) + str(self.id) + str(self.payload)
        checksum = 0
        for char in data:
            checksum = (checksum + ord(char)) % 256
        self.checksum = checksum
        return checksum
    
    def pack(self):
        """Convert packet to bytes for transmission"""
        self.calculate_checksum()
        
        # Create header
        header = "NFNET/%d %s ID:%d TIME:%d CHK:%d\n" % (
            self.version,
            self.type,
            self.id,
            self.timestamp,
            self.checksum
        )
        
        # Add options if any
        if self.options:
            options_line = "OPTIONS:"
            for key, value in self.options.items():
                options_line += " %s=%s;" % (key, value)
            header += options_line.rstrip(';') + "\n"
        
        # End of header
        header += "\n"
        
        # Combine header and payload
        return header + str(self.payload)
    
    @classmethod
    def unpack(cls, data):
        """Parse bytes back into a Packet object"""
        lines = data.split('\n')
        
        if len(lines) < 2:
            return None
        
        # Parse first line (mandatory header)
        first_line = lines[0].strip().split()
        if len(first_line) < 6:
            return None
        
        version_str = first_line[0]  # NFNET/1
        version = int(version_str.split('/')[1]) if '/' in version_str else 1
        packet_type = first_line[1]
        
        # Extract fields
        packet_id = 0
        timestamp = 0
        checksum = 0
        
        for field in first_line[2:]:
            if ':' in field:
                key, value = field.split(':', 1)
                if key == 'ID':
                    packet_id = int(value)
                elif key == 'TIME':
                    timestamp = int(value)
                elif key == 'CHK':
                    checksum = int(value)
        
        # Parse options if present
        options = {}
        payload_start = 1  # After first line
        
        if len(lines) > 1 and lines[1].startswith('OPTIONS:'):
            options_line = lines[1][8:].strip()
            if options_line:
                options_parts = options_line.split(';')
                for part in options_parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        options[key.strip()] = value.strip()
            payload_start = 2
        
        # Get payload (everything after header)
        payload = '\n'.join(lines[payload_start:])
        
        # Create packet
        packet = cls(packet_type, payload, options)
        packet.version = version
        packet.id = packet_id
        packet.timestamp = timestamp
        packet.checksum = checksum
        
        return packet
    
    def verify(self):
        """Verify packet integrity"""
        calculated = self.calculate_checksum()
        return calculated == self.checksum
    
    def __str__(self):
        return "[Packet %s:%d] %s" % (self.type, self.id, 
                                     self.payload[:50] + "..." if len(str(self.payload)) > 50 else self.payload)


class MessageHandler:
    """Handle different message types"""
    
    @staticmethod
    def create_ping():
        """Create a ping packet"""
        return Packet("PING", "PING")
    
    @staticmethod
    def create_pong():
        """Create a pong response"""
        return Packet("PONG", "PONG")
    
    @staticmethod
    def create_data(data, content_type="text/plain"):
        """Create a data packet"""
        return Packet("DATA", data, {"Content-Type": content_type})
    
    @staticmethod
    def create_route_command(command, params):
        """Create a routing command packet"""
        return Packet("ROUTE", str(params), {"Command": command})
    
    @staticmethod
    def create_error(code, message):
        """Create an error packet"""
        return Packet("ERROR", message, {"Code": str(code)})