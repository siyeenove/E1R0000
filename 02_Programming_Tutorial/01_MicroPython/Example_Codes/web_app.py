"""
eArm Robotic Arm Web Control System
"""

from machine import Pin
import time
import network
import socket
import gc
import _thread

# ==================== WiFi Setup ====================
WIFI_SSID = "eArm"
AP_IP = "192.168.4.1"

buzzer_state = False

def setup_wifi():
    """Configure ESP32 as WiFi Access Point"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=WIFI_SSID, authmode=network.AUTH_OPEN)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    
    for i in range(10):
        if ap.active():
            print("WiFi AP active")
            break
        time.sleep(0.5)
    
    print("=" * 40)
    print("SSID: " + WIFI_SSID)
    print("IP: " + AP_IP)
    print("=" * 40)
    return ap

# ==================== Control Functions ====================
def handle_command(params):
    """Process control commands"""
    global buzzer_state
    
    # Servo A
    if 'a_minus' in params:
        print("Press the - button of servo_A.") if params['a_minus'] == '1' else print("Release the - button of servo_A.")
    elif 'a_plus' in params:
        print("Press the + button of servo_A.") if params['a_plus'] == '1' else print("Release the + button of servo_A.")
    # Servo B
    elif 'b_minus' in params:
        print("Press the - button of servo_B.") if params['b_minus'] == '1' else print("Release the - button of servo_B.")
    elif 'b_plus' in params:
        print("Press the + button of servo_B.") if params['b_plus'] == '1' else print("Release the + button of servo_B.")
    # Servo C
    elif 'c_minus' in params:
        print("Press the - button of servo_C.") if params['c_minus'] == '1' else  print("Release the - button of servo_C.")
    elif 'c_plus' in params:
        print("Press the + button of servo_C.") if params['c_plus'] == '1' else print("Release the + button of servo_C.")
    # Servo D
    elif 'd_minus' in params:
        print("Press the - button of servo_D.") if params['d_minus'] == '1' else print("Release the - button of servo_D.")
    elif 'd_plus' in params:
        print("Press the + button of servo_D.") if params['d_plus'] == '1' else print("Release the + button of servo_D.")
    # Buzzer - Use different status codes
    elif 'buzzer' in params:
        if params['buzzer'] == 'on':
            buzzer_state = True
            print("Buzzer ON")
        elif params['buzzer'] == 'off':
            buzzer_state = False
            print("Buzzer OFF")
    return ""

def parse_request(req):
    """Extract URL parameters from HTTP request"""
    lines = req.split('\n')
    if lines:
        first = lines[0].split(' ')
        if len(first) > 1 and '?' in first[1]:
            query = first[1].split('?')[1]
            return {k:v for k,v in (p.split('=',1) for p in query.split('&') if '=' in p)}
    return {}

def send_response(client, content, ctype="text/html"):
    """Send HTTP response"""
    try:
        resp = f"HTTP/1.1 200 OK\r\nContent-Type: {ctype}\r\nConnection: close\r\n\r\n{content}"
        client.send(resp)
        client.close()
    except:
        pass

# ==================== HTML Generation ====================
def generate_html():
    """Generate HTML with current buzzer state"""
    wifi_status = "WiFi: Connected"  
    
    # Set the initial value based on the current buzzer status
    buzzer_class = "buzzer-btn" if buzzer_state else "buzzer-off"
    buzzer_icon = "🔊" if buzzer_state else "🔇"
    
    return f"""<!DOCTYPE html>
    <html><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>eArm</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
    body{{font-family:Arial,sans-serif;background:#1a1a2e;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
    .container{{width:100%;max-width:500px;background:white;padding:20px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.4)}}
    .header{{text-align:center;margin-bottom:15px;padding-bottom:15px;border-bottom:2px solid #eee}}
    h1{{color:#333;margin:0 0 10px 0;font-size:28px}}
    .status{{background:#f0f8ff;padding:12px;border-radius:10px;text-align:center;margin-bottom:20px;font-size:16px;font-weight:bold}}
    .wifi-connected{{color:#27ae60;background:#d5f4e6;border-left:5px solid #27ae60}}
    .servo-list{{display:flex;flex-direction:column;gap:15px;margin-bottom:10px}}
    .servo-card{{background:#f8f9fa;padding:15px;border-radius:15px;border:2px solid #e9ecef;display:flex;align-items:center;justify-content:space-between;height:100px}}
    .servo-label{{display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;padding:0 15px}}
    .servo-icon{{font-size:32px;margin-bottom:5px}}
    .control-btn{{width:70px;height:70px;border:none;border-radius:12px;font-size:30px;font-weight:bold;cursor:pointer;user-select:none;touch-action:manipulation;display:flex;align-items:center;justify-content:center;transition:transform 0.1s}}
    .control-btn:active{{transform:scale(0.95)}}
    .minus-btn{{background:#e74c3c;color:white}}
    .minus-btn.active{{background:#c0392b}}
    .plus-btn{{background:#2ecc71;color:white}}
    .plus-btn.active{{background:#27ae60}}
    .function-buttons{{display:grid;grid-template-columns:1fr;gap:12px;margin-top:25px}}
    .func-btn{{padding:18px;border:none;border-radius:12px;font-size:18px;font-weight:bold;cursor:pointer;color:white;display:flex;align-items:center;justify-content:center;gap:10px}}
    .buzzer-btn{{background:#f39c12}}
    .buzzer-off{{background:#7f8c8d}}
    .footer{{text-align:center;color:#7f8c8d;font-size:14px;padding-top:15px;margin-top:15px;border-top:1px solid #eee}}
    </style></head>
    <body>
    <div class="container">
    <div class="header"><h1>eArm</h1></div>
    <div class="status wifi-connected">{wifi_status}</div>
    <div class="servo-list">
    <div class="servo-card">
    <button class="control-btn minus-btn" id="a_minus" onmousedown="h('a','minus')" onmouseup="r('a','minus')" ontouchstart="h('a','minus')" ontouchend="r('a','minus')">➖</button>
    <div class="servo-label"><div class="servo-icon">🔄</div></div>
    <button class="control-btn plus-btn" id="a_plus" onmousedown="h('a','plus')" onmouseup="r('a','plus')" ontouchstart="h('a','plus')" ontouchend="r('a','plus')">➕</button>
    </div>
    <div class="servo-card">
    <button class="control-btn minus-btn" id="b_minus" onmousedown="h('b','minus')" onmouseup="r('b','minus')" ontouchstart="h('b','minus')" ontouchend="r('b','minus')">➖</button>
    <div class="servo-label"><div class="servo-icon">🦾</div></div>
    <button class="control-btn plus-btn" id="b_plus" onmousedown="h('b','plus')" onmouseup="r('b','plus')" ontouchstart="h('b','plus')" ontouchend="r('b','plus')">➕</button>
    </div>
    <div class="servo-card">
    <button class="control-btn minus-btn" id="c_minus" onmousedown="h('c','minus')" onmouseup="r('c','minus')" ontouchstart="h('c','minus')" ontouchend="r('c','minus')">➖</button>
    <div class="servo-label"><div class="servo-icon">🦾</div></div>
    <button class="control-btn plus-btn" id="c_plus" onmousedown="h('c','plus')" onmouseup="r('c','plus')" ontouchstart="h('c','plus')" ontouchend="r('c','plus')">➕</button>
    </div>
    <div class="servo-card">
    <button class="control-btn minus-btn" id="d_minus" onmousedown="h('d','minus')" onmouseup="r('d','minus')" ontouchstart="h('d','minus')" ontouchend="r('d','minus')">➖</button>
    <div class="servo-label"><div class="servo-icon">🫳</div></div>
    <button class="control-btn plus-btn" id="d_plus" onmousedown="h('d','plus')" onmouseup="r('d','plus')" ontouchstart="h('d','plus')" ontouchend="r('d','plus')">➕</button>
    </div>
    </div>
    <div class="function-buttons">
    <button class="func-btn {buzzer_class}" id="buzzerButton" onclick="t()">
    <span id="buzzerIcon">{buzzer_icon}</span>
    <span id="buzzerText">BUZZER</span>
    </button>
    </div>
    <div class="footer"><p>eArm Control System</p></div>
    </div>
    <script>
    var buzzerState = {str(buzzer_state).lower()};
    function h(s,d){{e(s+'_'+d).classList.add('active');f(s,d,'1')}}
    function r(s,d){{e(s+'_'+d).classList.remove('active');f(s,d,'0')}}
    function f(s,d,st){{fetch('/?'+s+'_'+d+'='+st,{{cache:'no-cache'}}).catch(()=>{{}})}}
    function t(){{
    buzzerState = !buzzerState;
    var b = e('buzzerButton');
    var i = e('buzzerIcon');
    var t = e('buzzerText');
    if(buzzerState){{
    b.className = 'func-btn buzzer-btn';
    i.textContent = '🔊';
    fetch('/?buzzer=on',{{cache:'no-cache'}});
    }}else{{
    b.className = 'func-btn buzzer-off';
    i.textContent = '🔇';
    fetch('/?buzzer=off',{{cache:'no-cache'}});
    }}
    }}
    function e(id){{return document.getElementById(id)}}
    function u(){{fetch('/?status_check=1').then(()=>{{}}).catch(()=>{{}});setTimeout(u,10000)}}
    window.onload = u;
    window.onbeforeunload = () => {{['a','b','c','d'].forEach(s => ['minus','plus'].forEach(d => f(s,d,'0')))}}
    </script>
    </body></html>"""

# ==================== Main Program ====================
def main():
    """Main program loop"""
    print("Starting eArm Control System...")
    ap = setup_wifi()
    
    # Setup server
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind(('0.0.0.0', 80))
    except Exception as e:
        print("Bind error:", e)
        return
    
    s.listen(5)
    print("Server on port 80")
    print("Connect to: " + WIFI_SSID)
    print("URL: http://" + AP_IP)
    
    while True:
        try:
            s.settimeout(0.1)
            try:
                client, addr = s.accept()
                req = client.recv(1024).decode()
                
                if req:
                    if '?' in req:
                        params = parse_request(req)
                        if 'status_check' in params:
                            send_response(client, "OK", "text/plain")
                        else:
                            handle_command(params)
                            send_response(client, "", "text/plain")
                    else:
                        html = generate_html()
                        send_response(client, html, "text/html")
                else:
                    client.close()
            except OSError:
                pass
            
            gc.collect()
            
        except Exception as e:
            print("Error:", e)
            try:
                client.close()
            except:
                pass

# ==================== Entry Point ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
