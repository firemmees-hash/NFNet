"""
NFNET Web Server - Simplified 2012 Style
"""

import socket
import threading
import os
import time
import urllib
import urllib2
import re
import base64

class WebServer:
    """Simple HTTP server with web proxy"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.server_socket = None
        
        # Base directory for resources
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        
        # Create resources directory if it doesn't exist
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def start(self):
        """Start the web server"""
        if self.running:
            print "[WEB] Server already running"
            return False
        
        print "[WEB] Starting web interface on port %s" % self.config.intranet_port
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.listen_ip, self.config.intranet_port))
            self.server_socket.listen(10)
            
            self.running = True
            
            # Start server thread
            server_thread = threading.Thread(target=self._run_server)
            server_thread.daemon = True
            server_thread.start()
            
            print "[WEB] Web interface started"
            print "[WEB] http://127.0.0.1:%s" % self.config.intranet_port
            return True
            
        except Exception as e:
            print "[WEB ERROR] Failed to start: %s" % str(e)
            return False
    
    def stop(self):
        """Stop the web server"""
        print "[WEB] Stopping web interface..."
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print "[WEB] Web interface stopped"
        return True
    
    def _run_server(self):
        """Run the HTTP server"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.settimeout(10)
                
                # Handle request in new thread
                thread = threading.Thread(target=self._handle_request, args=(client_socket, address))
                thread.daemon = True
                thread.start()
                
            except:
                break
    
    def _handle_request(self, client_socket, address):
        """Handle HTTP request"""
        try:
            # Receive request
            request_data = client_socket.recv(8192)
            if not request_data:
                return
            
            # Parse request line
            lines = request_data.split('\r\n')
            if not lines:
                return
            
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) < 2:
                return
            
            method = parts[0]
            path = parts[1]
            
            print "[WEB] %s %s" % (method, path)
            
            # Handle different paths
            if path == '/':
                self._serve_main_page(client_socket)
            elif path.startswith('/proxy?'):
                self._handle_proxy(client_socket, path)
            elif path == '/logo.png':
                self._serve_logo(client_socket)
            elif path.startswith('/fetch?'):
                self._handle_proxy(client_socket, path.replace('/fetch?', '/proxy?'))
            else:
                self._serve_local_file(client_socket, path)
                
        except Exception as e:
            print "[WEB ERROR] %s" % str(e)
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _serve_main_page(self, client_socket):
        """Serve main page - 2012 style"""
        # Check if logo exists
        logo_path = os.path.join(self.base_dir, 'logo.png')
        logo_exists = os.path.exists(logo_path)
        
        # Simple HTML - No formatting issues
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>NFNET</title>
    <meta charset="UTF-8">
    <style>
        body {
            background: white;
            margin: 40px;
            font-family: Tahoma, Arial, sans-serif;
            font-size: 14px;
        }
        .logo {
            text-align: center;
            margin: 20px 0 40px 0;
        }
        .logo img {
            max-width: 90%%;
            max-height: 200px;
            height: auto;
        }
        .search {
            text-align: center;
            margin: 30px 0;
        }
        .search input {
            width: 600px;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #999;
            font-family: Tahoma, Arial;
        }
        .search button {
            padding: 10px 20px;
            font-size: 16px;
            background: #f0f0f0;
            border: 1px solid #999;
            cursor: pointer;
            font-family: Tahoma, Arial;
        }
        .search button:hover {
            background: #e0e0e0;
        }
        .info {
            position: fixed;
            bottom: 10px;
            left: 10px;
            color: #666;
            font-size: 11px;
        }
        .links {
            text-align: center;
            margin: 20px;
            color: #666;
        }
        .links a {
            color: #0066cc;
            text-decoration: none;
            margin: 0 10px;
        }
        .links a:hover {
            text-decoration: underline;
        }
    </style>
    <script>
        function go() {
            var url = document.getElementById('url').value;
            if (!url) return;
            
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                url = 'http://' + url;
            }
            
            window.location = '/proxy?url=' + encodeURIComponent(url);
        }
        
        function handleKey(e) {
            if (e.keyCode == 13) go();
        }
    </script>
</head>
<body>
    <div class="logo">
''' + ('<img src="/logo.png" alt="NFNET">' if logo_exists else '<div style="font-size: 24px; color: #333;">NFNET</div>') + '''
    </div>
    
    <div class="search">
        <input type="text" id="url" placeholder="http://example.com" onkeypress="handleKey(event)">
        <button onclick="go()">Go</button>
    </div>
    
    <div class="links">
        <a href="/proxy?url=http://google.com">Google</a>
        <a href="/proxy?url=http://wikipedia.org">Wikipedia</a>
        <a href="/proxy?url=http://textfiles.com">Textfiles</a>
        <a href="/proxy?url=http://example.com">Example</a>
    </div>
    
    <div class="info">
        NFNET v''' + str(self.config.protocol_version) + '''<br>
        ''' + time.strftime("%Y-%m-%d %H:%M:%S") + '''<br>
        127.0.0.1:''' + str(self.config.intranet_port) + '''
    </div>
</body>
</html>'''
        
        # Send response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Server: NFNET/1.0\r\n"
        response += "Content-Type: text/html; charset=UTF-8\r\n"
        response += "Content-Length: " + str(len(html)) + "\r\n"
        response += "Connection: close\r\n\r\n"
        client_socket.send(response)
        client_socket.send(html)
    
    def _serve_logo(self, client_socket):
        """Serve logo"""
        logo_path = os.path.join(self.base_dir, 'logo.png')
        
        if not os.path.exists(logo_path):
            # Return 404
            self._send_404(client_socket)
            return
        
        try:
            with open(logo_path, 'rb') as f:
                image_data = f.read()
            
            response = "HTTP/1.1 200 OK\r\n"
            response += "Server: NFNET/1.0\r\n"
            response += "Content-Type: image/png\r\n"
            response += "Content-Length: " + str(len(image_data)) + "\r\n"
            response += "Connection: close\r\n\r\n"
            client_socket.send(response)
            client_socket.send(image_data)
            
        except:
            self._send_404(client_socket)
    
    def _handle_proxy(self, client_socket, path):
        """Handle web proxy requests"""
        try:
            # Extract URL
            query = path.split('?', 1)[1]
            params = {}
            for part in query.split('&'):
                if '=' in part:
                    key, val = part.split('=', 1)
                    params[key] = urllib.unquote(val)
            
            url = params.get('url', '')
            if not url:
                self._send_error(client_socket, "No URL specified")
                return
            
            # Fix relative URLs
            if url.startswith('/'):
                # Try to get base from referrer
                url = 'http:/' + url
            
            # Add protocol if missing
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            
            print "[PROXY] Fetching: " + url
            
            # Fetch with timeout
            opener = urllib2.build_opener()
            opener.addheaders = [
                ('User-Agent', 'NFNET/1.0'),
                ('Accept', 'text/html,image/*,*/*;q=0.8'),
            ]
            
            response = opener.open(url, timeout=15)
            content = response.read()
            content_type = response.headers.get('Content-Type', 'text/html').split(';')[0]
            
            # Process HTML to fix links
            if 'text/html' in content_type:
                content = self._process_html(content, url)
            
            # Send response
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "Server: NFNET/1.0\r\n"
            response_headers += "Content-Type: " + content_type + "\r\n"
            response_headers += "Content-Length: " + str(len(content)) + "\r\n"
            response_headers += "Connection: close\r\n"
            response_headers += "Access-Control-Allow-Origin: *\r\n"
            response_headers += "\r\n"
            
            client_socket.send(response_headers)
            client_socket.send(content)
            
        except Exception as e:
            print "[PROXY ERROR] " + str(e)
            self._send_error(client_socket, "Proxy error: " + str(e))
    
    def _process_html(self, html, base_url):
        """Process HTML to work through proxy"""
        # Get base domain for relative URLs
        base_domain = ''
        if '://' in base_url:
            base_domain = base_url.split('://')[1].split('/')[0]
        
        # Simple replacements
        html = html.replace('<head>', '<head><base href="' + base_url + '">')
        
        # Fix relative URLs in src and href
        patterns = [
            ('src="/([^"])"', 'src="/proxy?url=http://' + base_domain + '/\\1"'),
            ('href="/([^"])"', 'href="/proxy?url=http://' + base_domain + '/\\1"'),
            ('src="(http[^"]+)"', 'src="/proxy?url=\\1"'),
            ('href="(http[^"]+)"', 'href="/proxy?url=\\1"'),
        ]
        
        for pattern, replacement in patterns:
            try:
                html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
            except:
                pass
        
        # Add NFNET header
        header = '<!-- NFNET Proxy: ' + base_url + ' -->\n'
        return header + html
    
    def _serve_local_file(self, client_socket, path):
        """Serve local file"""
        # Security check
        if '..' in path:
            self._send_404(client_socket)
            return
        
        # Clean path
        clean_path = path.lstrip('/')
        file_path = os.path.join(self.base_dir, clean_path)
        
        if not os.path.exists(file_path):
            self._send_404(client_socket)
            return
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Guess content type
            ext = os.path.splitext(file_path)[1].lower()
            types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.html': 'text/html',
                '.htm': 'text/html',
                '.txt': 'text/plain',
                '.css': 'text/css',
                '.js': 'application/javascript',
            }
            content_type = types.get(ext, 'application/octet-stream')
            
            response = "HTTP/1.1 200 OK\r\n"
            response += "Server: NFNET/1.0\r\n"
            response += "Content-Type: " + content_type + "\r\n"
            response += "Content-Length: " + str(len(content)) + "\r\n"
            response += "Connection: close\r\n\r\n"
            
            client_socket.send(response)
            client_socket.send(content)
            
        except:
            self._send_404(client_socket)
    
    def _send_error(self, client_socket, message):
        """Send error page"""
        html = '<html><body style="font-family: Tahoma; padding: 40px;"><h3>Error</h3><p>' + message + '</p><p><a href="/">Back</a></p></body></html>'
        
        response = "HTTP/1.1 500 Error\r\n"
        response += "Server: NFNET/1.0\r\n"
        response += "Content-Type: text/html\r\n"
        response += "Content-Length: " + str(len(html)) + "\r\n"
        response += "Connection: close\r\n\r\n"
        
        client_socket.send(response)
        client_socket.send(html)
    
    def _send_404(self, client_socket):
        """Send 404 page"""
        html = '<html><body style="font-family: Tahoma; padding: 40px;"><h3>404 Not Found</h3><p><a href="/">Back to NFNET</a></p></body></html>'
        
        response = "HTTP/1.1 404 Not Found\r\n"
        response += "Server: NFNET/1.0\r\n"
        response += "Content-Type: text/html\r\n"
        response += "Content-Length: " + str(len(html)) + "\r\n"
        response += "Connection: close\r\n\r\n"
        
        client_socket.send(response)
        client_socket.send(html)