import socket
import ipaddress
import netifaces
import numpy as np
from scipy.signal import savgol_filter

from pythonosc import dispatcher
from pythonosc import osc_server

signal_history = []
WINDOW_SIZE=5

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
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Function to apply Savitzky-Golay filter to denoise the signal
def savitzky_golay_filter(data, window_size=WINDOW_SIZE, order=3):
    return savgol_filter(data, window_size, order)

# Function to calculate concentration metrics based on alpha and beta correlation
def calculate_concentration_metrics(data):
    # Assume the data format: [Delta, Theta, Alpha, Beta, Gamma]
    delta = data[:, 0]
    theta = data[:, 1]
    alpha = data[:, 2]
    beta = data[:, 3]
    gamma = data[:, 4]
    
    # Calculate correlation between alpha and beta. From 0 to 1.
    correlation_alpha_beta = (np.corrcoef(alpha, beta)[0, 1] + 1) / 2 

    theta_beta_ratio = np.mean(beta) / np.mean(delta)
    min_value = 1.5
    max_value = 6
    theta_beta_ratio = max(0, min(1, 1 - (theta_beta_ratio - min_value) / (max_value - min_value)))


    concentartion = theta_beta_ratio
    
    return concentartion

# Function to calculate concentration metrics based on alpha and beta correlation
def calculate_concentration(data):
    # Assume the data format: [Delta, Theta, Alpha, Beta, Gamma]
    alpha = data[:, 2]
    beta = data[:, 3]
    
    # Calculate correlation between alpha and beta
    correlation_alpha_beta = np.corrcoef(alpha, beta)[0, 1]
    
    # Derive concentration metrics based on correlation (you can customize this part)
    # concentration_metric = some_function_of_correlation(correlation_alpha_beta)
    
    return correlation_alpha_beta

# Callback function to receive and process OSC messages
def callback(address, *args):
    global signal_history
    
    # Assume the data format: [Delta, Theta, Alpha, Beta, Gamma]
    signal = np.array(args)
    
    # # Denoise the signal using moving average filter
    # denoised_signal = moving_average(signal)

     # Apply Savitzky-Golay filter to denoise the signal
    denoised_signal = savitzky_golay_filter(signal, order=3)  # Adjust order as needed
    
    # Add the denoised signal to the history
    signal_history.append(denoised_signal)
    
    # Keep only the last N=10 data signals in the history
    signal_history = signal_history[-10:]
    
    # Calculate concentration metrics
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