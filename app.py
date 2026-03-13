from flask import Flask, request, jsonify
import sqlite3
import hashlib
import os

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# 密码加密
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 注册接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 检查用户名是否已存在
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': '用户名已存在'})
    
    # 插入新用户
    hashed_password = hash_password(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '注册成功'})

# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 查找用户
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': '用户名或密码错误'})
    
    # 验证密码
    hashed_password = hash_password(password)
    if hashed_password != user[2]:
        return jsonify({'success': False, 'message': '用户名或密码错误'})
    
    return jsonify({'success': True, 'message': '登录成功'})

# 静态文件服务
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    init_db()
    # 确保静态文件目录存在
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, host='0.0.0.0', port=5000)