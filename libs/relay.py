"""
NFNET Relay Server
Handles network connections and routing
"""

import socket
import threading
import time
import Queue

class RelayServer:
    """Main relay server for NFNET protocol"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.sockets = []
        self.clients = {}
        self.message_queue = Queue.Queue()
        self.cache = {}
        self.lock = threading.Lock()
        
        # Web server
        from web_server import WebServer
        self.web_server = WebServer(config)
        
        # Statistics
        self.stats = {
            'connections': 0,
            'packets_sent': 0,
            'packets_received': 0,
            'errors': 0,
            'start_time': 0
        }
        
        print "[RELAY] Initialized on port %s" % config.relay_port
    
    def start(self):
        """Start the relay server and web interface"""
        if self.running:
            print "[RELAY] Server already running"
            return False
        
        print "[RELAY] Starting server..."
        
        try:
            # Start web server first
            if not self.web_server.start():
                print "[RELAY WARN] Could not start web interface"
            
            # Create main socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.listen_ip, self.config.relay_port))
            self.server_socket.listen(self.config.max_clients)
            
            self.running = True
            self.stats['start_time'] = time.time()
            
            # Start threads
            self.accept_thread = threading.Thread(target=self._accept_connections)
            self.accept_thread.daemon = True
            self.accept_thread.start()
            
            self.process_thread = threading.Thread(target=self._process_messages)
            self.process_thread.daemon = True
            self.process_thread.start()
            
            print "[RELAY] Server started successfully on port %s" % self.config.relay_port
            print "[RELAY] Web interface: http://127.0.0.1:%s" % self.config.intranet_port
            return True
            
        except Exception as e:
            print "[RELAY ERROR] Failed to start: %s" % str(e)
            return False
    
    def stop(self):
        """Stop the relay server and web interface"""
        print "[RELAY] Stopping server..."
        self.running = False
        
        # Stop web server
        self.web_server.stop()
        
        # Close all sockets
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        
        if hasattr(self, 'server_socket'):
            try:
                self.server_socket.close()
            except:
                pass
        
        print "[RELAY] Server stopped"
        return True
    
    def _accept_connections(self):
        """Accept incoming connections"""
        print "[RELAY] Waiting for connections..."
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.settimeout(self.config.timeout)
                
                # Check if we have capacity
                with self.lock:
                    if len(self.clients) >= self.config.max_clients:
                        print "[RELAY] Connection limit reached, rejecting %s" % str(address)
                        client_socket.close()
                        continue
                
                # Handle client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                with self.lock:
                    self.clients[address] = {
                        'socket': client_socket,
                        'thread': client_thread,
                        'connected_at': time.time(),
                        'packets': 0
                    }
                    self.stats['connections'] += 1
                
                print "[RELAY] New connection from %s:%s" % (address[0], address[1])
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # Only print if we're supposed to be running
                    print "[RELAY ERROR] Accept failed: %s" % str(e)
                break
    
    def _handle_client(self, client_socket, address):
        """Handle communication with a client"""
        buffer = ""
        
        while self.running:
            try:
                # Receive data
                data = client_socket.recv(self.config.buffer_size)
                if not data:
                    break
                
                buffer += data
                self.stats['packets_received'] += 1
                
                # Process complete messages (delimited by newlines)
                while '\n\n' in buffer:
                    message, buffer = buffer.split('\n\n', 1)
                    
                    # Parse packet
                    from protocol import Packet
                    packet = Packet.unpack(message + '\n\n')
                    
                    if packet:
                        if packet.verify():
                            # Add to processing queue
                            self.message_queue.put({
                                'client': address,
                                'socket': client_socket,
                                'packet': packet
                            })
                        else:
                            print "[RELAY] Invalid checksum from %s" % str(address)
                            self.stats['errors'] += 1
                
                # Send queued responses
                # This would handle outgoing messages
                
            except socket.timeout:
                continue
            except socket.error:
                break
            except Exception as e:
                print "[RELAY ERROR] Client handler: %s" % str(e)
                break
        
        # Cleanup
        try:
            client_socket.close()
        except:
            pass
        
        with self.lock:
            if address in self.clients:
                del self.clients[address]
        
        print "[RELAY] Connection closed: %s:%s" % (address[0], address[1])
    
    def _process_messages(self):
        """Process incoming messages"""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1)
                
                client = message['client']
                socket = message['socket']
                packet = message['packet']
                
                # Handle based on packet type
                response = self._handle_packet(packet)
                
                if response:
                    # Send response
                    socket.send(response.pack())
                    self.stats['packets_sent'] += 1
                    
                    # Update client stats
                    with self.lock:
                        if client in self.clients:
                            self.clients[client]['packets'] += 1
                
            except Queue.Empty:
                continue
            except Exception as e:
                print "[RELAY ERROR] Message processor: %s" % str(e)
    
    def _handle_packet(self, packet):
        """Handle different packet types"""
        from protocol import MessageHandler
        
        if packet.type == "PING":
            print "[RELAY] Ping from client %s" % packet.id
            return MessageHandler.create_pong()
        
        elif packet.type == "DATA":
            # Process data packet
            content_type = packet.options.get('Content-Type', 'text/plain')
            
            # Check cache
            cache_key = hash(str(packet.payload))
            if self.config.enable_cache and cache_key in self.cache:
                print "[RELAY] Cache hit for data packet"
                return self.cache[cache_key]
            
            # Process based on content type
            if 'html' in content_type:
                processed = self._process_html(packet.payload)
            elif 'javascript' in content_type or 'js' in content_type:
                processed = self._process_javascript(packet.payload)
            elif 'image' in content_type:
                processed = self._process_image(packet.payload, content_type)
            else:
                processed = packet.payload
            
            # Create response
            response = MessageHandler.create_data(processed, content_type)
            
            # Cache if enabled
            if self.config.enable_cache:
                self.cache[cache_key] = response
                # Limit cache size
                if len(self.cache) > self.config.cache_size:
                    # Remove oldest (simple approach)
                    if self.cache:
                        del self.cache[next(iter(self.cache))]
            
            return response
        
        elif packet.type == "ROUTE":
            # Handle routing commands
            command = packet.options.get('Command', '')
            print "[RELAY] Routing command: %s" % command
            return MessageHandler.create_data("Route command received: %s" % command)
        
        else:
            # Unknown packet type
            return MessageHandler.create_error(400, "Unknown packet type: %s" % packet.type)
    
    def _process_html(self, html):
        """Process HTML content"""
        # Simple HTML processing - add NFNET header
        processed = "<!-- Processed by NFNET Relay -->\n" + html
        return processed
    
    def _process_javascript(self, js):
        """Process JavaScript content"""
        print "[RELAY] Processing JavaScript (%s bytes)" % len(js)
        
        # Simple JS processing - add comment and basic minification
        processed = "/* NFNET JS Processor - Build 143 */\n"
        
        # Remove single line comments (simple approach)
        lines = js.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('//') and stripped:
                processed += line + '\n'
        
        return processed
    
    def _process_image(self, image_data, content_type):
        """Process image data"""
        print "[RELAY] Processing image (%s, %s bytes)" % (content_type, len(image_data))
        
        # For now, just pass through
        # In a real implementation, this might resize or convert images
        return image_data
    
    def get_stats(self):
        """Get server statistics"""
        with self.lock:
            stats = self.stats.copy()
            stats['uptime'] = time.time() - stats['start_time']
            stats['clients'] = len(self.clients)
            stats['cache_size'] = len(self.cache)
            stats['queue_size'] = self.message_queue.qsize()
        
        return stats