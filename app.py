from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify, send_file
from flask_socketio import SocketIO, emit
from datetime import datetime
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
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
            cursor: default;
        }

        .lore-message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
            color: #ffffff;
            padding: 40px 60px;
            border: 1px solid #333;
            border-radius: 2px;
            box-shadow: 0 0 60px rgba(0,0,0,0.95), inset 0 0 80px rgba(255,255,255,0.03);
            z-index: 2000;
            text-align: center;
            font-family: 'Courier Prime', monospace;
            font-size: 18px;
            letter-spacing: 3px;
            text-transform: uppercase;
            opacity: 0;
            transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            max-width: 600px;
        }

        .lore-label {
            font-size: 11px;
            letter-spacing: 2px;
            color: #666;
            margin-bottom: 15px;
        }

        .lore-code {
            font-size: 16px;
            letter-spacing: 2px;
            color: #4CAF50;
            word-break: break-all;
            line-height: 1.6;
        }

        .lore-message.show {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }

        .lore-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 1999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s;
        }

        .lore-overlay.show {
            opacity: 1;
            pointer-events: auto;
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
            cursor: default;
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
            cursor: default;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 15px;
            border: 1px solid #444;
            border-radius: 2px;
            font-size: 11px;
            cursor: default;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            animation: blink 2s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
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

        .btn-small {
            padding: 6px 12px;
            font-size: 10px;
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
            min-height: 150px;
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
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
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

        .page-navigation {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            padding: 10px;
            background: #0a0a0a;
            border: 1px solid #222;
            border-radius: 2px;
        }

        .page-counter {
            font-size: 11px;
            letter-spacing: 1px;
            color: #888;
        }

        .page-nav-buttons {
            display: flex;
            gap: 8px;
        }

        .book-content {
            color: #b0b0b0;
            line-height: 1.8;
            margin-bottom: 20px;
            min-height: 180px;
            font-size: 13px;
            position: relative;
            padding: 15px;
            background: #0a0a0a;
            border: 1px solid #222;
            border-radius: 2px;
        }

        .page-date {
            font-size: 10px;
            color: #555;
            letter-spacing: 1px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .page-list {
            margin-bottom: 20px;
        }

        .page-item {
            background: #0a0a0a;
            padding: 12px 15px;
            margin-bottom: 8px;
            border-left: 2px solid #333;
            border-radius: 2px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
            cursor: pointer;
        }

        .page-item:hover {
            border-left-color: #666;
            background: #111;
        }

        .page-item-content {
            flex: 1;
        }

        .page-item-title {
            font-size: 11px;
            letter-spacing: 1px;
            color: #888;
            text-transform: uppercase;
        }

        .page-item-preview {
            font-size: 12px;
            color: #b0b0b0;
            margin-top: 5px;
        }

        .page-item-actions {
            display: flex;
            gap: 8px;
        }

        .signature-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #222;
        }

        .signature-display {
            background: #0a0a0a;
            padding: 15px;
            border-left: 2px solid #4CAF50;
            border-radius: 2px;
            margin-top: 10px;
        }

        .signature-text {
            font-size: 12px;
            color: #4CAF50;
            letter-spacing: 1px;
            font-style: italic;
        }

        .signature-date {
            font-size: 10px;
            color: #666;
            margin-top: 5px;
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
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
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

        @keyframes fadeOut {
            from { opacity: 1; transform: scale(1); }
            to { opacity: 0; transform: scale(0.9); }
        }

        .deleting {
            animation: fadeOut 0.3s ease-out forwards;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            animation: fadeIn 0.3s;
        }

        .modal-content {
            background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
            margin: 5% auto;
            padding: 30px;
            border: 1px solid #333;
            border-radius: 2px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 0 50px rgba(0,0,0,0.9);
            position: relative;
        }

        .close {
            color: #888;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s;
        }

        .close:hover {
            color: #ffffff;
        }

        .modal h2 {
            font-family: 'Courier Prime', monospace;
            font-size: 18px;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 20px;
            color: #ffffff;
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
                <div class="status-indicator" onclick="showLore()">
                    <div class="status-dot"></div>
                    <span>LIVE</span>
                </div>
                <span class="user-label" onclick="showLore2()">IDENTITY: {{ session['user'] }}</span>
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
            <form id="createBookForm">
                <div class="form-group">
                    <label>Document Title</label>
                    <input type="text" name="title" id="bookTitle" required placeholder="Enter classification...">
                </div>
                <div class="form-group">
                    <label>Security Clearance</label>
                    <select name="visibility" id="bookVisibility">
                        <option value="public">PUBLIC ACCESS</option>
                        <option value="private">RESTRICTED</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Commentary Protocol</label>
                    <select name="allow_comments" id="bookComments">
                        <option value="yes">ENABLED</option>
                        <option value="no">DISABLED</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">Initialize Entry</button>
            </form>
        </div>
        {% endif %}

        <div class="books-grid" id="booksGrid">
            <!-- Books will be inserted here dynamically -->
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

    <!-- Lore Overlay -->
    <div class="lore-overlay" id="loreOverlay" onclick="hideLore()"></div>
    <div class="lore-message" id="loreMessage">
        <div class="lore-label">◆ ENCRYPTED TRANSMISSION DETECTED ◆</div>
        <div class="lore-code">uggcf://jjj.lbhghor.pbz/@Cbba-x8d</div>
    </div>
    <div class="lore-message" id="loreMessage2">
        <div class="lore-label">◆ ENCRYPTED TRANSMISSION DETECTED ◆</div>
        <div class="lore-code">tavreru=Cpu?hgvq/rbV74a9w14-nnJTGUM_V_sb69QLmtQE6ZsKQp3ujM58u/1/q/tnezhpbq/mzp.rtybbt.fpboq//:fggu</div>
    </div>

    <!-- Add Page Modal -->
    <div id="addPageModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeAddPageModal()">&times;</span>
            <h2>Add New Page</h2>
            <div class="divider"></div>
            <form id="addPageForm">
                <input type="hidden" id="pageBookId">
                <div class="form-group">
                    <label>Page Content</label>
                    <textarea id="pageContent" required placeholder="Enter page data..."></textarea>
                </div>
                <button type="submit" class="btn btn-success">Add Page</button>
            </form>
        </div>
    </div>

    <!-- Edit Page Modal -->
    <div id="editPageModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeEditPageModal()">&times;</span>
            <h2>Edit Page</h2>
            <div class="divider"></div>
            <form id="editPageForm">
                <input type="hidden" id="editPageBookId">
                <input type="hidden" id="editPageIndex">
                <div class="form-group">
                    <label>Page Content</label>
                    <textarea id="editPageContent" required placeholder="Enter page data..."></textarea>
                </div>
                <button type="submit" class="btn btn-success">Update Page</button>
            </form>
        </div>
    </div>

    <!-- Sign Off Modal -->
    <div id="signOffModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeSignOffModal()">&times;</span>
            <h2>Sign Off Document</h2>
            <div class="divider"></div>
            <form id="signOffForm">
                <input type="hidden" id="signOffBookId">
                <div class="form-group">
                    <label>Signature Message</label>
                    <textarea id="signOffMessage" required placeholder="Enter your signature message..."></textarea>
                </div>
                <button type="submit" class="btn btn-success">Sign Document</button>
            </form>
        </div>
    </div>

    <script>
        function showLore() {
            document.getElementById('loreOverlay').classList.add('show');
            document.getElementById('loreMessage').classList.add('show');
            setTimeout(hideLore, 3500);
        }

        function showLore2() {
            document.getElementById('loreOverlay').classList.add('show');
            document.getElementById('loreMessage2').classList.add('show');
            setTimeout(hideLore, 4500);
        }

        function hideLore() {
            document.getElementById('loreOverlay').classList.remove('show');
            document.getElementById('loreMessage').classList.remove('show');
            document.getElementById('loreMessage2').classList.remove('show');
        }

        {% if 'user' in session %}
        const socket = io();
        const isAdmin = {{ 'true' if session.get('is_admin') else 'false' }};
        let currentPages = {}; // Track current page for each book

        socket.on('connect', function() {
            console.log('Connected to real-time server');
            socket.emit('request_initial_data');
        });

        socket.on('initial_data', function(data) {
            renderBooks(data.books, data.comments, data.likes);
        });

        socket.on('book_created', function(data) {
            addBookToGrid(data.book_id, data.book, data.comments, data.likes);
            currentPages[data.book_id] = 0;
        });

        socket.on('book_deleted', function(data) {
            removeBookFromGrid(data.book_id);
            delete currentPages[data.book_id];
        });

        socket.on('book_updated', function(data) {
            updateBook(data.book_id, data.book);
        });

        socket.on('comment_added', function(data) {
            addComment(data.book_id, data.comment);
        });

        socket.on('like_updated', function(data) {
            updateLikeCount(data.book_id, data.likes);
        });

        socket.on('page_added', function(data) {
            refreshBook(data.book_id, data.book);
        });

        socket.on('page_deleted', function(data) {
            refreshBook(data.book_id, data.book);
        });

        function renderBooks(books, comments, likes) {
            const grid = document.getElementById('booksGrid');
            grid.innerHTML = '';

            for (const [bookId, book] of Object.entries(books)) {
                if (book.visibility === 'public' || isAdmin) {
                    addBookToGrid(bookId, book, comments[bookId] || [], likes[bookId] || []);
                    currentPages[bookId] = 0;
                }
            }
        }

        function refreshBook(bookId, book) {
            const bookCard = document.querySelector(`[data-book-id="${bookId}"]`);
            if (bookCard) {
                const pageIndex = currentPages[bookId] || 0;
                updateBookPages(bookId, book, pageIndex);
            }
        }

        function updateBookPages(bookId, book, pageIndex) {
            const contentDiv = bookCard.querySelector('.book-content');
            const navDiv = bookCard.querySelector('.page-navigation');

            if (book.pages && book.pages.length > 0) {
                const page = book.pages[pageIndex];
                contentDiv.textContent = page.content;
                navDiv.querySelector('.page-counter').textContent = `PAGE ${pageIndex + 1} OF ${book.pages.length}`;
            }
        }

        function addBookToGrid(bookId, book, bookComments, bookLikes) {
            const grid = document.getElementById('booksGrid');
            const bookCard = createBookCard(bookId, book, bookComments, bookLikes);
            grid.insertAdjacentHTML('afterbegin', bookCard);
        }

        function removeBookFromGrid(bookId) {
            const bookCard = document.querySelector(`[data-book-id="${bookId}"]`);
            if (bookCard) {
                bookCard.classList.add('deleting');
                setTimeout(() => bookCard.remove(), 300);
            }
        }

        function updateBook(bookId, book) {
            const bookCard = document.querySelector(`[data-book-id="${bookId}"]`);
            if (bookCard) {
                const badge = bookCard.querySelector('.badge');
                badge.className = `badge badge-${book.visibility}`;
                badge.textContent = book.visibility.toUpperCase();
            }
        }

        function addComment(bookId, comment) {
            const commentsContainer = document.querySelector(`[data-book-id="${bookId}"] .comments-list`);
            if (commentsContainer) {
                const commentHtml = `
                    <div class="comment">
                        <div class="comment-author">◆ ${comment.author}</div>
                        <div class="comment-text">${comment.text}</div>
                    </div>
                `;
                commentsContainer.insertAdjacentHTML('beforeend', commentHtml);
            }
        }

        function updateLikeCount(bookId, likes) {
            const likeElement = document.getElementById('like-' + bookId);
            if (likeElement) {
                likeElement.textContent = likes.length;
            }
        }

        function createBookCard(bookId, book, bookComments, bookLikes) {
            const commentsHtml = bookComments.map(c => `
                <div class="comment">
                    <div class="comment-author">◆ ${c.author}</div>
                    <div class="comment-text">${c.text}</div>
                </div>
            `).join('');

            const pages = book.pages || [];
            const currentPageContent = pages.length > 0
                ? `<div class="page-date">Added: ${pages[0].created}</div>${pages[0].content}`
                : 'No pages yet...';
            const pageCount = pages.length;

            const pageNavigation = `
                <div class="page-navigation">
                    <div class="page-counter">PAGE 1 OF ${pageCount || 1}</div>
                    <div class="page-nav-buttons">
                        <button class="btn btn-small btn-primary" onclick="prevPage('${bookId}')">◀ PREV</button>
                        <button class="btn btn-small btn-primary" onclick="nextPage('${bookId}')">NEXT ▶</button>
                    </div>
                </div>
            `;

            const adminPageButtons = isAdmin ? `
                <button class="btn btn-primary btn-small" onclick="openAddPageModal('${bookId}')">+ Page</button>
                <button class="btn btn-danger btn-small" onclick="deletePage('${bookId}')">- Page</button>
                <button class="btn btn-primary btn-small" onclick="viewPages('${bookId}')">View All</button>
                <button class="btn btn-success btn-small" onclick="openSignOffModal('${bookId}')">Sign Off</button>
            ` : '';

            const signatureSection = book.signature ? `
                <div class="signature-section">
                    <h3 style="font-size: 12px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; opacity: 0.8;">◆ Document Signed ◆</h3>
                    <div class="signature-display">
                        <div class="signature-text">"${book.signature.message}"</div>
                        <div class="signature-date">— ${book.signature.author}, ${book.signature.date}</div>
                    </div>
                </div>
            ` : '';

            const adminButtons = isAdmin ? `
                <button class="btn btn-primary" onclick="toggleVisibility('${bookId}')">Access</button>
                <button class="btn btn-primary" onclick="toggleComments('${bookId}')">Comments</button>
                ${adminPageButtons}
                <button class="btn btn-danger" onclick="deleteBook('${bookId}')">Erase</button>
            ` : '';

            const commentSection = book.allow_comments ? `
                <div class="comment-section">
                    <h3>Transmissions</h3>
                    <div class="comments-list">
                        ${commentsHtml}
                    </div>
                    <form onsubmit="addComment(event, '${bookId}')">
                        <div class="form-group">
                            <textarea name="comment" placeholder="Transmit message..." rows="3" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-success">Send</button>
                    </form>
                </div>
            ` : `
                <div class="comment-section">
                    <p style="color: #444; font-size: 11px; letter-spacing: 1px;">TRANSMISSIONS LOCKED</p>
                </div>
            `;

            return `
                <div class="book-card" data-book-id="${bookId}">
                    <div class="book-header">
                        <img src="/logo" alt="Logo" class="book-logo">
                        <div class="book-title">${book.title}</div>
                    </div>
                    <span class="badge badge-${book.visibility}">${book.visibility.toUpperCase()}</span>
                    <div class="book-meta">Archived: ${book.created} | ID: #${bookId} | Pages: ${pageCount}</div>
                    ${pageCount > 0 ? pageNavigation : ''}
                    <div class="book-content">${currentPageContent}</div>
                    <div class="book-actions">
                        <button class="btn btn-primary" onclick="toggleLike('${bookId}')">
                            ◆ MARK (<span id="like-${bookId}">${bookLikes.length}</span>)
                        </button>
                        ${adminButtons}
                    </div>
                    ${signatureSection}
                    ${commentSection}
                </div>
            `;
        }

        function prevPage(bookId) {
            if (!currentPages[bookId]) currentPages[bookId] = 0;
            const bookCard = document.querySelector(`[data-book-id="${bookId}"]`);
            socket.emit('get_book', {book_id: bookId}, (book) => {
                if (book.pages && book.pages.length > 0) {
                    currentPages[bookId] = (currentPages[bookId] - 1 + book.pages.length) % book.pages.length;
                    updatePageDisplay(bookId, book);
                }
            });
        }

        function nextPage(bookId) {
            if (!currentPages[bookId]) currentPages[bookId] = 0;
            socket.emit('get_book', {book_id: bookId}, (book) => {
                if (book.pages && book.pages.length > 0) {
                    currentPages[bookId] = (currentPages[bookId] + 1) % book.pages.length;
                    updatePageDisplay(bookId, book);
                }
            });
        }

        function updatePageDisplay(bookId, book) {
            const bookCard = document.querySelector(`[data-book-id="${bookId}"]`);
            if (bookCard && book.pages && book.pages.length > 0) {
                const pageIndex = currentPages[bookId];
                const contentDiv = bookCard.querySelector('.book-content');
                const counterDiv = bookCard.querySelector('.page-counter');
                const page = book.pages[pageIndex];

                contentDiv.innerHTML = `
                    <div class="page-date">Added: ${page.created}</div>
                    ${page.content}
                `;
                counterDiv.textContent = `PAGE ${pageIndex + 1} OF ${book.pages.length}`;
            }
        }

        function openAddPageModal(bookId) {
            document.getElementById('pageBookId').value = bookId;
            document.getElementById('addPageModal').style.display = 'block';
        }

        function closeAddPageModal() {
            document.getElementById('addPageModal').style.display = 'none';
            document.getElementById('addPageForm').reset();
        }

        function openEditPageModal(bookId, pageIndex, content) {
            document.getElementById('editPageBookId').value = bookId;
            document.getElementById('editPageIndex').value = pageIndex;
            document.getElementById('editPageContent').value = content;
            document.getElementById('editPageModal').style.display = 'block';
        }

        function closeEditPageModal() {
            document.getElementById('editPageModal').style.display = 'none';
            document.getElementById('editPageForm').reset();
        }

        function openSignOffModal(bookId) {
            document.getElementById('signOffBookId').value = bookId;
            document.getElementById('signOffModal').style.display = 'block';
        }

        function closeSignOffModal() {
            document.getElementById('signOffModal').style.display = 'none';
            document.getElementById('signOffForm').reset();
        }

        function viewPages(bookId) {
            socket.emit('get_book', {book_id: bookId}, (book) => {
                if (book.pages && book.pages.length > 0) {
                    let pagesHtml = book.pages.map((page, index) => `
                        <div class="page-item" onclick="openEditPageModal('${bookId}', ${index}, \`${page.content.replace(/`/g, '\\`')}\`)">
                            <div class="page-item-content">
                                <div class="page-item-title">Page ${index + 1} - ${page.created}</div>
                                <div class="page-item-preview">${page.content.substring(0, 100)}...</div>
                            </div>
                            <div class="page-item-actions">
                                <button class="btn btn-danger btn-small" onclick="event.stopPropagation(); deletePageByIndex('${bookId}', ${index})">Delete</button>
                            </div>
                        </div>
                    `).join('');

                    alert('Page management coming in modal view');
                } else {
                    alert('No pages in this document yet.');
                }
            });
        }

        function deletePageByIndex(bookId, pageIndex) {
            if (confirm(`Delete page ${pageIndex + 1}?`)) {
                socket.emit('delete_page', {book_id: bookId, page_index: pageIndex});
            }
        }

        function deletePage(bookId) {
            if (!currentPages[bookId]) currentPages[bookId] = 0;
            socket.emit('get_book', {book_id: bookId}, (book) => {
                if (book.pages && book.pages.length > 0) {
                    const pageIndex = currentPages[bookId];
                    if (confirm(`Delete page ${pageIndex + 1}?`)) {
                        socket.emit('delete_page', {book_id: bookId, page_index: pageIndex});
                        if (currentPages[bookId] >= book.pages.length - 1 && currentPages[bookId] > 0) {
                            currentPages[bookId]--;
                        }
                    }
                }
            });
        }

        document.getElementById('addPageForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const bookId = document.getElementById('pageBookId').value;
            const content = document.getElementById('pageContent').value;

            socket.emit('add_page', {book_id: bookId, content: content});
            closeAddPageModal();
        });

        document.getElementById('editPageForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const bookId = document.getElementById('editPageBookId').value;
            const pageIndex = parseInt(document.getElementById('editPageIndex').value);
            const content = document.getElementById('editPageContent').value;

            socket.emit('edit_page', {book_id: bookId, page_index: pageIndex, content: content});
            closeEditPageModal();
        });

        document.getElementById('signOffForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const bookId = document.getElementById('signOffBookId').value;
            const message = document.getElementById('signOffMessage').value;

            socket.emit('sign_book', {book_id: bookId, message: message});
            closeSignOffModal();
        });

        function toggleLike(bookId) {
            socket.emit('toggle_like', {book_id: bookId});
        }

        function deleteBook(bookId) {
            if (confirm('Are you sure you want to erase this entry?')) {
                socket.emit('delete_book', {book_id: bookId});
            }
        }

        function toggleVisibility(bookId) {
            socket.emit('toggle_visibility', {book_id: bookId});
        }

        function toggleComments(bookId) {
            socket.emit('toggle_comments', {book_id: bookId});
        }

        function addComment(event, bookId) {
            event.preventDefault();
            const form = event.target;
            const comment = form.comment.value;
            socket.emit('add_comment', {book_id: bookId, comment: comment});
            form.reset();
        }

        {% if session.get('is_admin') %}
        document.getElementById('createBookForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = {
                title: document.getElementById('bookTitle').value,
                visibility: document.getElementById('bookVisibility').value,
                allow_comments: document.getElementById('bookComments').value
            };
            socket.emit('create_book', formData);
            this.reset();
        });
        {% endif %}

        // Close modal when clicking outside
        window.onclick = function(event) {
            const addModal = document.getElementById('addPageModal');
            const editModal = document.getElementById('editPageModal');
            const signModal = document.getElementById('signOffModal');

            if (event.target == addModal) {
                closeAddPageModal();
            }
            if (event.target == editModal) {
                closeEditPageModal();
            }
            if (event.target == signModal) {
                closeSignOffModal();
            }
        }
        {% endif %}
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

# WebSocket event handlers
@socketio.on('request_initial_data')
def handle_initial_data():
    emit('initial_data', {
        'books': books,
        'comments': comments,
        'likes': likes
    })

@socketio.on('get_book')
def handle_get_book(data, callback):
    book_id = data['book_id']
    if book_id in books:
        callback(books[book_id])

@socketio.on('create_book')
def handle_create_book(data):
    if not session.get('is_admin'):
        return

    book_id = str(len(books) + 1)
    book = {
        'title': data['title'],
        'visibility': data['visibility'],
        'allow_comments': data['allow_comments'] == 'yes',
        'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'pages': []
    }
    books[book_id] = book
    comments[book_id] = []
    likes[book_id] = []

    socketio.emit('book_created', {
        'book_id': book_id,
        'book': book,
        'comments': [],
        'likes': []
    })

@socketio.on('add_page')
def handle_add_page(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']
    if book_id in books:
        page = {
            'content': data['content'],
            'created': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        if 'pages' not in books[book_id]:
            books[book_id]['pages'] = []
        books[book_id]['pages'].append(page)

        socketio.emit('page_added', {
            'book_id': book_id,
            'book': books[book_id]
        })

@socketio.on('edit_page')
def handle_edit_page(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']
    page_index = data['page_index']

    if book_id in books and 'pages' in books[book_id]:
        if 0 <= page_index < len(books[book_id]['pages']):
            books[book_id]['pages'][page_index]['content'] = data['content']
            books[book_id]['pages'][page_index]['edited'] = datetime.now().strftime('%Y-%m-%d %H:%M')

            socketio.emit('page_updated', {
                'book_id': book_id,
                'book': books[book_id]
            })

@socketio.on('sign_book')
def handle_sign_book(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']

    if book_id in books:
        books[book_id]['signature'] = {
            'message': data['message'],
            'author': session['user'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        socketio.emit('book_signed', {
            'book_id': book_id,
            'book': books[book_id]
        })

@socketio.on('delete_page')
def handle_delete_page(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']
    page_index = data['page_index']

    if book_id in books and 'pages' in books[book_id]:
        if 0 <= page_index < len(books[book_id]['pages']):
            books[book_id]['pages'].pop(page_index)

            socketio.emit('page_deleted', {
                'book_id': book_id,
                'book': books[book_id]
            })

@socketio.on('delete_book')
def handle_delete_book(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']
    if book_id in books:
        del books[book_id]
        if book_id in comments:
            del comments[book_id]
        if book_id in likes:
            del likes[book_id]

        socketio.emit('book_deleted', {'book_id': book_id})

@socketio.on('toggle_visibility')
def handle_toggle_visibility(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']
    if book_id in books:
        books[book_id]['visibility'] = 'private' if books[book_id]['visibility'] == 'public' else 'public'
        socketio.emit('book_updated', {
            'book_id': book_id,
            'book': books[book_id]
        })

@socketio.on('toggle_comments')
def handle_toggle_comments(data):
    if not session.get('is_admin'):
        return

    book_id = data['book_id']
    if book_id in books:
        books[book_id]['allow_comments'] = not books[book_id]['allow_comments']
        socketio.emit('book_updated', {
            'book_id': book_id,
            'book': books[book_id]
        })

@socketio.on('add_comment')
def handle_add_comment(data):
    if 'user' not in session:
        return

    book_id = data['book_id']
    if book_id in books and books[book_id]['allow_comments']:
        comment = {
            'author': session['user'],
            'text': data['comment'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        if book_id not in comments:
            comments[book_id] = []
        comments[book_id].append(comment)

        socketio.emit('comment_added', {
            'book_id': book_id,
            'comment': comment
        })

@socketio.on('toggle_like')
def handle_toggle_like(data):
    if 'user' not in session:
        return

    book_id = data['book_id']
    if book_id not in likes:
        likes[book_id] = []

    user = session['user']
    if user in likes[book_id]:
        likes[book_id].remove(user)
    else:
        likes[book_id].append(user)

    socketio.emit('like_updated', {
        'book_id': book_id,
        'likes': likes[book_id]
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
