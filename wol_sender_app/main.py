from flask import Flask, jsonify, request
import socket

app = Flask(__name__)

def send_wol(mac_address, broadcast_ip):
    # Clean the MAC address
    clean_mac = mac_address.replace(':', '').replace('-', '')
    if len(clean_mac) != 12:
        raise ValueError("Invalid MAC address")
        
    # Build the Magic Packet
    data = bytes.fromhex('FFFFFFFFFFFF' + clean_mac * 16)
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Send to the IP provided in the query parameter
        s.sendto(data, (broadcast_ip, 9))

@app.route('/wake/<mac>', methods=['GET'])
def wake(mac):
    # Get 'broadcast' from URL parameters, default to '255.255.255.255'
    broadcast_target = request.args.get('broadcast', '255.255.255.255')
    
    try:
        send_wol(mac, broadcast_target)
        return jsonify({
            "status": "sent",
            "mac": mac,
            "broadcast_address": broadcast_target
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6767)
