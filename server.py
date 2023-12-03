import socket
import ipaddress
import netifaces
import numpy as np
from scipy.signal import savgol_filter, coherence
import random

from pythonosc import dispatcher
from pythonosc import osc_server

signal_history = []
WINDOW_SIZE=100

def get_ip_and_subnet():
    # Get the name of the default socket interface
    interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
    # Get the IP address and netmask of the interface
    ip_info = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
    return ip_info['addr'], ip_info['netmask']

def calculate_broadcast_address(ip, netmask):
    # Create an IPv4 network object with the given IP and netmask
    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
    # Return the broadcast address of the network
    return str(network.broadcast_address)

# Function to apply moving average filter to denoise the signal
def moving_average(data, window_size=WINDOW_SIZE):
    if len(data) < window_size:
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')
    else:
        return data


# Function to apply Savitzky-Golay filter to denoise the signal
def savitzky_golay_filter(data, window_size=5, order=3):
    return savgol_filter(data, window_size, order)

# Function to calculate concentration metrics based on alpha and beta correlation
def calculate_concentration(data):
    # Assume the data format: [Delta, Theta, Alpha, Beta, Gamma]
    delta = data[:, 0]
    theta = data[:, 1]
    alpha = data[:, 2]
    beta = data[:, 3]
    gamma = data[:, 4]
    
    # Calculate correlation between alpha and beta. From 0 to 1.
    # coherence_alpha_beta = coherence(alpha, beta)

    theta_beta_ratio = np.mean(beta) / np.mean(delta)
    min_value = 1.5
    max_value = 6
    theta_beta_ratio = max(0, min(1, 1 - (theta_beta_ratio - min_value) / (max_value - min_value)))

    concentartion = theta_beta_ratio
    
    # return concentartion + (random.random() - 0.5)/50
    return concentartion


# Callback function to receive and process OSC messages
def callback(address, *args):
    global signal_history
    
    # Assume the data format: [Delta, Theta, Alpha, Beta, Gamma]
    signal = np.array(args)

    if len(signal_history) < WINDOW_SIZE:
        signal_history.append(signal)
    
    else:
        signal_history = moving_average(signal_history+[signal])
        # signal_history = savitzky_golay_filter(signal_history)

        # Keep only the last data signals in the history
        signal_history = signal_history[-WINDOW_SIZE:]
        
        # # Calculate concentration metrics
        concentration_metric = calculate_concentration(np.array(signal_history))
        
        # print(f"Received an OSC message at the address {address}: {args}")
        # print(f"Denoised Signal: {denoised_signal}")
        print(f"Concentration Metric: {concentration_metric}")

# Initialize OSC server and dispatcher
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/muse/eeg", callback)

ip, netmask = get_ip_and_subnet()
broadcast_address = calculate_broadcast_address(ip, netmask)

print(f"IP Address: {ip}")
print(f"Subnet Mask: {netmask}")
print(f"Broadcast Address: {broadcast_address}")

ip_address = ip
port = 5000

server = osc_server.ThreadingOSCUDPServer((ip_address, port), dispatcher)

print(f"Listening on {ip_address}:{port}")
server.serve_forever()



import asyncio
import websockets
import json

async def send_metric(websocket, path):
    global concentration_metric

    while True:
        await asyncio.sleep(1)  # Adjust the interval as needed
        await websocket.send(json.dumps({"concentration_metric": concentration_metric}))

start_server = websockets.serve(send_metric, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_sersver)
asyncio.get_event_loop().run_forever()
