# 🎯 InfoX-Tool 🔥

<p align="center">  
  <img src="https://img.shields.io/badge/Version-2.0.0-blue" alt="Version">  
  <img src="https://img.shields.io/badge/Python-3.8+-green" alt="Python">  
  <img src="https://img.shields.io/badge/Platform-Termux%2FLinux-yellow" alt="Platform">  
  <img src="https://img.shields.io/badge/License-MIT-red" alt="License">  
</p>  
<p align="center">  
  <b>Advanced Camera 📸 Location 📍 Device 📱 Video 🎞️ Hacking Tool for Educational Purposes Only</b>  
</p>  

---

📜 Hacker's Quote

"The quieter you become, the more you are able to hear." - Unknown Hacker

---

⚠️ DISCLAIMER

THIS TOOL IS CREATED FOR EDUCATIONAL AND SECURITY TESTING PURPOSES ONLY. THE DEVELOPER IS NOT RESPONSIBLE FOR ANY MISUSE OF THIS TOOL. USE IT ONLY ON SYSTEMS YOU OWN OR HAVE EXPLICIT PERMISSION TO TEST. UNAUTHORIZED ACCESS TO COMPUTER SYSTEMS IS ILLEGAL.

---

👨‍💻 Developer

Ꮥᴜᴅɪᴩ々Ꮥᴀʀᴋᴀʀ - Cyber Security Researcher & Developer

---

🚀 Features

- ✅ WAN Access - Works on any network worldwide
- ✅ Real Camera Capture - 3 photos + 5-second video
- ✅ Location Tracking - GPS coordinates with accuracy
- ✅ Device Fingerprinting - Complete device information
- ✅ IP Geolocation - City, country, ISP details
- ✅ QR Code Generation - Easy sharing with victims
- ✅ Multiple Tunnels - Cloudflare, Ngrok, Localhost.run
- ✅ Gallery Saving - Photos/videos saved to device
- ✅ Real-time Logging - Live data capture monitoring

---

📋 Prerequisites

- Termux App (Android)
- Python 3.8+
- Storage Permission
- Internet Connection

---

🛠️ Installation & Setup

1. **Update & Upgrade Termux**

```bash
pkg update && pkg upgrade -y
pkg install python -y
pkg install git -y
```

2. **Install Required Packages**

```bash
pkg install python python-pip -y
pip install --upgrade pip
```

3. **Install Python Dependencies**

```bash
pip install flask qrcode pillow colorama requests
```

4. **Install Tunnel Services**

```bash
pkg install cloudflared ngrok openssh -y
```

5. **Setup Storage Permission**

```bash
termux-setup-storage
```

---

📥 Download & Run

**Method 1: Clone Repository**

```bash
git clone https://github.com/sudip-sarkar-git/InfoX-Tool.git
cd InfoX-Tool
python3 InfoX-Tool.py
```

**Method 2: Direct Download**

```bash
curl -O https://github.com/sudip-sarkar-git/InfoX-Tool.git
python3 InfoX-Tool.py
```

**Method 3: Manual Creation**

```bash
nano InfoX-Tool.py
# Copy the code and save (Ctrl+X, Y, Enter)
python3 InfoX-Tool.py
```

---

🎯 Usage Guide

**Step 1: Run the Tool**

```bash
python3 InfoX-Tool.py
```

**Step 2: Choose Tunnel Option**

- Option 1: Auto (Recommended)
- Option 2: Cloudflare Only
- Option 3: Ngrok Only
- Option 4: Localhost.run Only

**Step 3: Share Link**

- Copy the generated URL
- Share via QR code or direct link
- Wait for victim to access

**Step 4: Monitor Captured Data**

- Real-time logging in terminal
- Photos/videos saved to gallery
- CSV report generated

---

📊 Captured Data

- 📍 Location: Latitude, Longitude, Accuracy
- 🌐 IP Info: IP Address, City, Country, ISP
- 📱 Device: User Agent, Screen Size, Platform
- 🖥️ Browser: Type, Version, Language
- 📸 Media: 3 Photos + 5-second Video
- ⏰ Timestamp: Access time and date

---

🗂️ Output Files

- `reward_qr.png` - QR code for sharing
- `reports.csv` - All captured data in CSV format
- `Photo_.jpg` - Captured photos in gallery
- `Video_.webm` - Captured videos in gallery

---

🔧 Troubleshooting

**Common Issues & Solutions**

1. **Tool not running:**

```bash
chmod +x InfoX-Tool.py
python3 InfoX-Tool.py
```

2. **Missing dependencies:**

```bash
pip install --force-reinstall flask qrcode pillow colorama requests
```

3. **Tunnel not working:**

```bash
pkg reinstall cloudflared ngrok -y
```

4. **Storage permission denied:**

```bash
termux-setup-storage
termux-storage-get /sdcard
```

5. **Port already in use:**

```bash
pkill -f python
python3 InfoX-Tool.py
```

---

🌐 Tunnel Services Explained

1. **Cloudflare Tunnel** ⭐

- Most reliable
- Free forever
- Fast connection
- URL: https://xxx.trycloudflare.com

2. **Ngrok Tunnel**

- Easy to use
- Good performance
- URL: https://xxx.ngrok.io

3. **Localhost.run**

- SSH-based
- No installation needed
- URL: https://xxx.localhost.run

---

📱 Victim Perspective

1. Sees fake reward page: "Congratulations! You won $500!"
2. Clicks "CLAIM YOUR REWARD NOW"
3. Grants camera permission
4. System automatically captures:
   - 3 photos from front camera
   - 5-second video recording
   - GPS location
   - Device information
   - IP address details

---

🔒 Security Features

- No data stored on external servers
- All data saved locally on your device
- Automatic media scanner update
- Multiple gallery backup locations
- Encrypted data transmission

---

⚡ Quick Commands Cheat Sheet

```bash
# Start tool
python3 InfoX-Tool.py

# Update tool
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt

# Fix permissions
chmod +x InfoX-Tool.py

# Clear cache
rm -rf reports.csv reward_qr.png

# Check services
cloudflared --version
ngrok --version
```

---

🎨 Customization

**Change Reward Amount:**

Edit the HTML template and change:

```html
<div class="reward">$500</div>
```

**Modify Gallery Paths:**

Edit the `GALLERY_PATHS` list in code.

**Add New Data Capture:**

Extend the JavaScript `collectedData` object.

---

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

🙏 Acknowledgements

- Open source community for amazing tools
- Beta testers for valuable feedback

---

<p align="center">  
  <b>Made with ❤️ by Ꮥᴜᴅɪᴩ々Ꮥᴀʀᴋᴀʀ</b>  
</p>  
<p align="center">  
  <i>"Knowledge is power, but wisdom is using it responsibly."</i>  
</p>  

---

🚨 Final Warning

THIS TOOL IS FOR LEGAL SECURITY TESTING AND EDUCATIONAL PURPOSES ONLY. USERS ARE SOLELY RESPONSIBLE FOR COMPLYING WITH ALL APPLICABLE LAWS. THE DEVELOPER ASSUMES NO LIABILITY FOR MISUSE.

---

© 2025 InfoX-Tool | Developed by Ꮥᴜᴅɪᴩ々Ꮥᴀʀᴋᴀʀ
