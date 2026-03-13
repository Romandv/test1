import http.server
import socketserver
import json
import hashlib
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': '用户名和密码不能为空'}).encode('utf-8'))
                return
            
            # 检查用户是否已存在
            if os.path.exists('users.json'):
                with open('users.json', 'r', encoding='utf-8') as f:
                    try:
                        users = json.load(f)
                    except json.JSONDecodeError:
                        users = {}
            else:
                users = {}
            
            if username in users:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': '用户名已存在'}).encode('utf-8'))
                return
            
            # 注册新用户
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            users[username] = hashed_password
            
            with open('users.json', 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': '注册成功'}).encode('utf-8'))
            return
        
        elif self.path == '/api/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': '用户名和密码不能为空'}).encode('utf-8'))
                return
            
            # 检查用户是否存在
            if os.path.exists('users.json'):
                with open('users.json', 'r', encoding='utf-8') as f:
                    try:
                        users = json.load(f)
                    except json.JSONDecodeError:
                        users = {}
            else:
                users = {}
            
            if username not in users:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': '用户名或密码错误'}).encode('utf-8'))
                return
            
            # 验证密码
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password != users[username]:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': '用户名或密码错误'}).encode('utf-8'))
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': '登录成功'}).encode('utf-8'))
            return
        
        # 处理其他POST请求
        super().do_POST()

if __name__ == '__main__':
    # 确保users.json文件存在
    if not os.path.exists('users.json'):
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    
    # 尝试不同的端口
    for port in range(PORT, PORT + 10):
        try:
            # 启动服务器
            with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
                print(f"服务器运行在 http://localhost:{port}")
                httpd.serve_forever()
        except OSError as e:
            if e.errno == 10048:  # 端口被占用
                print(f"端口 {port} 已被占用，尝试使用端口 {port + 1}")
                continue
            else:
                raise
        break