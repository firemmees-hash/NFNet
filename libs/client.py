"""
NFNET Client Module
For connecting to NFNET servers
"""
# -*- coding: utf-8 -*-
import socket
import time

class Client:
    """NFNET protocol client"""
    
    def __init__(self, host="127.0.0.1", port=28080):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.last_ping = 0
        
    def connect(self):
        """Connect to NFNET server"""
        try:
            print "[CLIENT] Connecting to %s:%s..." % (self.host, self.port)
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            self.connected = True
            print "[CLIENT] Connected successfully"
            return True
            
        except Exception as e:
            print "[CLIENT ERROR] Connection failed: %s" % str(e)
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        print "[CLIENT] Disconnected"
    
    def send_packet(self, packet):
        """Send a packet to the server"""
        if not self.connected:
            print "[CLIENT] Not connected"
            return None
        
        try:
            # Send packet
            data = packet.pack()
            self.socket.send(data)
            
            # Wait for response
            response_data = self._receive_response()
            if response_data:
                from protocol import Packet
                return Packet.unpack(response_data)
            
        except Exception as e:
            print "[CLIENT ERROR] Send failed: %s" % str(e)
        
        return None
    
    def _receive_response(self):
        """Receive response from server"""
        try:
            # Simple receive with timeout
            self.socket.settimeout(5)
            data = self.socket.recv(8192)
            return data
        except socket.timeout:
            print "[CLIENT] Receive timeout"
            return None
        except Exception as e:
            print "[CLIENT ERROR] Receive failed: %s" % str(e)
            return None
    
    def ping(self):
        """Send ping to server"""
        from protocol import MessageHandler
        
        packet = MessageHandler.create_ping()
        response = self.send_packet(packet)
        
        if response and response.type == "PONG":
            self.last_ping = time.time()
            return True
        else:
            return False
    
    def send_data(self, data, content_type="text/plain"):
        """Send data to server"""
        from protocol import MessageHandler
        
        packet = MessageHandler.create_data(data, content_type)
        return self.send_packet(packet)