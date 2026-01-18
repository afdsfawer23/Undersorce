from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify, send_file
from datetime import datetime
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Admin credentials
ADMIN_PASSCODE = "19312687lL1"

# In-memory storage
books = {}
comments = {}
likes = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Underscore - Enter the Archive</title>
    <link rel="icon" href="{{ url_for('serve_logo') }}" type="image/png">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Roboto+Mono:wght@300;400;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto Mono', monospace;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(255,255,255,.03) 2px,
                    rgba(255,255,255,.03) 4px
                );
            pointer-events: none;
            z-index: 1;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }

        .glitch {
            position: relative;
            animation: glitch 3s infinite;
        }

        @keyframes glitch {
            0%, 100% { transform: translate(0); }
            33% { transform: translate(-2px, 2px); }
            66% { transform: translate(2px, -2px); }
        }

        .header {
            background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
            color: #ffffff;
            padding: 25px 30px;
            border: 1px solid #333;
            border-radius: 2px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(0,0,0,0.8), inset 0 0 40px rgba(255,255,255,0.02);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, transparent, #666, transparent);
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .logo {
            width: 50px;
            height: 50px;
            filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
            animation: pulse 4s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; filter: drop-shadow(0 0 15px rgba(255,255,255,0.5)); }
        }

        .site-title {
            font-family: 'Courier Prime', monospace;
            font-size: 28px;
            letter-spacing: 3px;
            text-transform: uppercase;
            font-weight: 700;
            text-shadow: 0 0 10px rgba(255,255,255,0.3);
        }

        .user-info {
            display: flex;
            gap: 15px;
            align-items: center;
            font-size: 13px;
            letter-spacing: 1px;
        }

        .user-label {
            opacity: 0.7;
            border: 1px solid #444;
            padding: 8px 15px;
            border-radius: 2px;
        }

        .btn {
            padding: 10px 25px;
            border: 1px solid #ffffff;
            background: transparent;
            color: #ffffff;
            border-radius: 2px;
            cursor: pointer;
            font-size: 12px;
            font-family: 'Roboto Mono', monospace;
            letter-spacing: 2px;
            text-transform: uppercase;
            transition: all 0.3s;
            font-weight: 400;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: #ffffff;
            transition: left 0.3s;
            z-index: -1;
        }

        .btn:hover::before {
            left: 0;
        }

        .btn:hover {
            color: #000000;
            box-shadow: 0 0 15px rgba(255,255,255,0.5);
        }

        .btn-primary {
            border-color: #ffffff;
        }

        .btn-danger {
            border-color: #888;
            color: #888;
        }

        .btn-danger:hover {
            border-color: #ffffff;
            color: #000000;
        }

        .btn-success {
            background: #ffffff;
            color: #000000;
        }

        .btn-success:hover {
            background: #000000;
            color: #ffffff;
        }

        .login-container {
            background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
            color: #ffffff;
            padding: 60px;
            border: 1px solid #333;
            border-radius: 2px;
            max-width: 500px;
            margin: 120px auto;
            box-shadow: 0 0 40px rgba(0,0,0,0.9), inset 0 0 60px rgba(255,255,255,0.02);
            text-align: center;
            position: relative;
        }

        .login-container::before {
            content: '';
            position: absolute;
            top: -1px;
            left: -1px;
            right: -1px;
            bottom: -1px;
            background: linear-gradient(45deg, transparent, #333, transparent);
            z-index: -1;
            border-radius: 2px;
        }

        .login-logo {
            width: 100px;
            height: 100px;
            margin: 0 auto 30px;
            display: block;
            filter: drop-shadow(0 0 20px rgba(255,255,255,0.4));
            animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .login-container h2 {
            margin-bottom: 15px;
            color: #ffffff;
            font-family: 'Courier Prime', monospace;
            font-size: 24px;
            letter-spacing: 5px;
            text-transform: uppercase;
        }

        .login-subtitle {
            font-size: 11px;
            letter-spacing: 2px;
            opacity: 0.6;
            margin-bottom: 40px;
            text-transform: uppercase;
        }

        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #ffffff;
            font-weight: 400;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.8;
        }

        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #333;
            border-radius: 2px;
            font-size: 13px;
            background: #0a0a0a;
            color: #ffffff;
            font-family: 'Roboto Mono', monospace;
            transition: all 0.3s;
        }

        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #666;
            box-shadow: 0 0 10px rgba(255,255,255,0.1);
        }

        .form-group textarea {
            min-height: 200px;
            resize: vertical;
            line-height: 1.6;
        }

        .books-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .book-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            color: #ffffff;
            padding: 25px;
            border: 1px solid #222;
            border-radius: 2px;
            box-shadow: 0 0 30px rgba(0,0,0,0.7), inset 0 0 40px rgba(255,255,255,0.02);
            transition: all 0.3s;
            position: relative;
        }

        .book-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 2px;
            height: 100%;
            background: linear-gradient(180deg, transparent, #444, transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .book-card:hover {
            transform: translateY(-5px);
            border-color: #444;
            box-shadow: 0 5px 40px rgba(0,0,0,0.9), inset 0 0 60px rgba(255,255,255,0.03);
        }

        .book-card:hover::before {
            opacity: 1;
        }

        .book-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #222;
        }

        .book-logo {
            width: 30px;
            height: 30px;
            opacity: 0.7;
        }

        .book-title {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            flex: 1;
            letter-spacing: 1px;
            font-family: 'Courier Prime', monospace;
        }

        .book-meta {
            color: #666;
            font-size: 10px;
            margin-bottom: 15px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .book-content {
            color: #b0b0b0;
            line-height: 1.8;
            margin-bottom: 20px;
            max-height: 180px;
            overflow: hidden;
            font-size: 13px;
            position: relative;
        }

        .book-content::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 40px;
            background: linear-gradient(transparent, #0d0d0d);
        }

        .book-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            padding-top: 15px;
            border-top: 1px solid #222;
        }

        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 2px;
            font-size: 10px;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            border: 1px solid;
        }

        .badge-public {
            background: transparent;
            color: #ffffff;
            border-color: #ffffff;
        }

        .badge-private {
            background: transparent;
            color: #666;
            border-color: #666;
        }

        .comment-section {
            margin-top: 25px;
            padding-top: 25px;
            border-top: 1px solid #222;
        }

        .comment-section h3 {
            font-size: 12px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 15px;
            opacity: 0.8;
        }

        .comment {
            background: #0a0a0a;
            padding: 15px;
            border-radius: 2px;
            margin-bottom: 12px;
            border-left: 2px solid #333;
            transition: border-color 0.3s;
        }

        .comment:hover {
            border-left-color: #666;
        }

        .comment-author {
            font-weight: 700;
            color: #ffffff;
            font-size: 12px;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .comment-text {
            color: #b0b0b0;
            line-height: 1.6;
            font-size: 12px;
        }

        .like-count {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #ffffff;
        }

        .admin-panel {
            background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
            color: #ffffff;
            padding: 30px;
            border: 1px solid #333;
            border-radius: 2px;
            margin-bottom: 30px;
            box-shadow: 0 0 30px rgba(0,0,0,0.8), inset 0 0 50px rgba(255,255,255,0.02);
            position: relative;
        }

        .admin-panel::before {
            content: 'RESTRICTED ACCESS';
            position: absolute;
            top: 10px;
            right: 20px;
            font-size: 9px;
            letter-spacing: 2px;
            color: #444;
            text-transform: uppercase;
        }

        .admin-panel h2 {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            font-family: 'Courier Prime', monospace;
            font-size: 16px;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        .admin-logo {
            width: 35px;
            height: 35px;
            opacity: 0.8;
        }

        .error {
            color: #ffffff;
            margin-top: 15px;
            padding: 12px;
            background: #1a0000;
            border: 1px solid #440000;
            border-radius: 2px;
            font-size: 11px;
            letter-spacing: 1px;
        }

        .success {
            color: #ffffff;
            background: #001a00;
            border: 1px solid #004400;
            margin-top: 15px;
            padding: 12px;
            border-radius: 2px;
            font-size: 11px;
            letter-spacing: 1px;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #333, transparent);
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if 'user' in session %}
        <div class="header">
            <div class="header-left">
                <img src="{{ url_for('serve_logo') }}" alt="Underscore Logo" class="logo">
                <div class="site-title glitch">Underscore</div>
            </div>
            <div class="user-info">
                <span class="user-label">IDENTITY: {{ session['user'] }}</span>
                <a href="{{ url_for('logout') }}"><button class="btn btn-danger">Disconnect</button></a>
            </div>
        </div>

        {% if session.get('is_admin') %}
        <div class="admin-panel">
            <h2>
                <img src="{{ url_for('serve_logo') }}" alt="Logo" class="admin-logo">
                Archive Entry Creation
            </h2>
            <div class="divider"></div>
            <form method="POST" action="{{ url_for('create_book') }}">
                <div class="form-group">
                    <label>Document Title</label>
                    <input type="text" name="title" required placeholder="Enter classification...">
                </div>
                <div class="form-group">
                    <label>Document Content</label>
                    <textarea name="content" required placeholder="Enter encrypted data..."></textarea>
                </div>
                <div class="form-group">
                    <label>Security Clearance</label>
                    <select name="visibility">
                        <option value="public">PUBLIC ACCESS</option>
                        <option value="private">RESTRICTED</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Commentary Protocol</label>
                    <select name="allow_comments">
                        <option value="yes">ENABLED</option>
                        <option value="no">DISABLED</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">Initialize Entry</button>
            </form>
        </div>
        {% endif %}

        <div class="books-grid">
            {% for book_id, book in books.items() %}
            {% if book['visibility'] == 'public' or session.get('is_admin') %}
            <div class="book-card">
                <div class="book-header">
                    <img src="{{ url_for('serve_logo') }}" alt="Logo" class="book-logo">
                    <div class="book-title">{{ book['title'] }}</div>
                </div>
                <span class="badge badge-{{ book['visibility'] }}">{{ book['visibility'].upper() }}</span>
                <div class="book-meta">Archived: {{ book['created'] }} | ID: #{{ book_id }}</div>
                <div class="book-content">{{ book['content'][:200] }}...</div>

                <div class="book-actions">
                    <button class="btn btn-primary" onclick="toggleLike('{{ book_id }}')">
                        ◆ MARK (<span id="like-{{ book_id }}">{{ likes.get(book_id, []) | length }}</span>)
                    </button>
                    {% if session.get('is_admin') %}
                    <form method="POST" action="{{ url_for('toggle_visibility', book_id=book_id) }}" style="display:inline;">
                        <button type="submit" class="btn btn-primary">Access</button>
                    </form>
                    <form method="POST" action="{{ url_for('toggle_comments', book_id=book_id) }}" style="display:inline;">
                        <button type="submit" class="btn btn-primary">Comments</button>
                    </form>
                    <form method="POST" action="{{ url_for('delete_book', book_id=book_id) }}" style="display:inline;">
                        <button type="submit" class="btn btn-danger">Erase</button>
                    </form>
                    {% endif %}
                </div>

                {% if book['allow_comments'] %}
                <div class="comment-section">
                    <h3>Transmissions</h3>
                    {% for comment in comments.get(book_id, []) %}
                    <div class="comment">
                        <div class="comment-author">◆ {{ comment['author'] }}</div>
                        <div class="comment-text">{{ comment['text'] }}</div>
                    </div>
                    {% endfor %}

                    <form method="POST" action="{{ url_for('add_comment', book_id=book_id) }}">
                        <div class="form-group">
                            <textarea name="comment" placeholder="Transmit message..." rows="3" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-success">Send</button>
                    </form>
                </div>
                {% else %}
                <div class="comment-section">
                    <p style="color: #444; font-size: 11px; letter-spacing: 1px;">TRANSMISSIONS LOCKED</p>
                </div>
                {% endif %}
            </div>
            {% endif %}
            {% endfor %}
        </div>

        {% else %}
        <div class="login-container">
            <img src="{{ url_for('serve_logo') }}" alt="Underscore Logo" class="login-logo">
            <h2 class="glitch">Underscore</h2>
            <p class="login-subtitle">Classified Archive System</p>
            <form method="POST" action="{{ url_for('login') }}">
                <div class="form-group">
                    <label>Administrative Credentials</label>
                    <input type="password" name="passcode" placeholder="Enter security key...">
                </div>
                <button type="submit" name="login_type" value="admin" class="btn btn-primary" style="width:100%; margin-bottom:15px;">Access Archive</button>
                <button type="submit" name="login_type" value="guest" class="btn btn-success" style="width:100%;">Anonymous Entry</button>
                {% if error %}
                <p class="error">{{ error }}</p>
                {% endif %}
            </form>
        </div>
        {% endif %}
    </div>

    <script>
        function toggleLike(bookId) {
            fetch('/like/' + bookId, {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    document.getElementById('like-' + bookId).textContent = data.likes;
                });
        }
    </script>
</body>
</html>
'''

@app.route('/logo')
def serve_logo():
    logo_path = os.path.join(BASE_DIR, 'Logo.png')
    return send_file(logo_path, mimetype='image/png')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, books=books, comments=comments, likes=likes)

@app.route('/login', methods=['POST'])
def login():
    login_type = request.form.get('login_type')

    if login_type == 'admin':
        passcode = request.form.get('passcode')
        if passcode == ADMIN_PASSCODE:
            session['user'] = 'Admin'
            session['is_admin'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(HTML_TEMPLATE, error="INVALID CREDENTIALS - ACCESS DENIED", books=books, comments=comments, likes=likes)
    else:
        session['user'] = 'Guest'
        session['is_admin'] = False
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create_book', methods=['POST'])
def create_book():
    if not session.get('is_admin'):
        return redirect(url_for('index'))

    book_id = str(len(books) + 1)
    books[book_id] = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'visibility': request.form.get('visibility'),
        'allow_comments': request.form.get('allow_comments') == 'yes',
        'created': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    comments[book_id] = []
    likes[book_id] = []
    return redirect(url_for('index'))

@app.route('/toggle_visibility/<book_id>', methods=['POST'])
def toggle_visibility(book_id):
    if not session.get('is_admin'):
        return redirect(url_for('index'))

    if book_id in books:
        books[book_id]['visibility'] = 'private' if books[book_id]['visibility'] == 'public' else 'public'
    return redirect(url_for('index'))

@app.route('/toggle_comments/<book_id>', methods=['POST'])
def toggle_comments(book_id):
    if not session.get('is_admin'):
        return redirect(url_for('index'))

    if book_id in books:
        books[book_id]['allow_comments'] = not books[book_id]['allow_comments']
    return redirect(url_for('index'))

@app.route('/delete_book/<book_id>', methods=['POST'])
def delete_book(book_id):
    if not session.get('is_admin'):
        return redirect(url_for('index'))

    if book_id in books:
        del books[book_id]
        if book_id in comments:
            del comments[book_id]
        if book_id in likes:
            del likes[book_id]
    return redirect(url_for('index'))

@app.route('/add_comment/<book_id>', methods=['POST'])
def add_comment(book_id):
    if 'user' not in session:
        return redirect(url_for('index'))

    if book_id in books and books[book_id]['allow_comments']:
        comment_text = request.form.get('comment')
        if book_id not in comments:
            comments[book_id] = []
        comments[book_id].append({
            'author': session['user'],
            'text': comment_text,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
    return redirect(url_for('index'))

@app.route('/like/<book_id>', methods=['POST'])
def like_book(book_id):
    if 'user' not in session:
        return jsonify({'likes': 0})

    if book_id not in likes:
        likes[book_id] = []

    user = session['user']
    if user in likes[book_id]:
        likes[book_id].remove(user)
    else:
        likes[book_id].append(user)

    return jsonify({'likes': len(likes[book_id])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)