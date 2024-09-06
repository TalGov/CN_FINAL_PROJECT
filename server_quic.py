import time
import random
import socket
import os
import argparse
from tools import generate_random_data, plot_data
from classes import Packet, Ack

class Server:
    def __init__(self, loss_probability=0.00, host='localhost', port=5000):
        self.client_address = None
        self.loss_probability = loss_probability
        self.packets = []
        self.acknowledged = set()
        self.acknowledged.add(-1)
        self.rtt_estimates = []
        self.packet_sent_times = {}
        self.lost_packets = []
        self.srtt = 0
        self.rtt_var = 0
        self.pto = 1
        self.last_largest_acknowledged = -2
        self.transfer_time = 0
        self.data = ["", [], []]
        self.timeout = 0.03

        # Server socket setup
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        print(f"Server listening on {host}:{port}")

    def load_file(self, data):
        packet_size = 1024*5  # Define the size of each packet (0.1KB in this case)
        num_packets = (len(data) + packet_size - 1) // packet_size  # Calculate total number of packets
        for seq_num in range(num_packets):
            packet_data = data[seq_num * packet_size: (seq_num + 1) * packet_size]
            self.packets.append(Packet(seq_num, packet_data))
        print(f"Loaded {len(self.packets)} packets from raw data")

    def detect_lost_packets(self, start_time, loss_detection_method):
        lost_packets_methods = {
            'timeout': [],
            'out_of_order': []
        }

        self.data[1].append(self.last_largest_acknowledged)
        self.data[2].append(time.time() - start_time)

        t0 = max(self.srtt, max(self.rtt_estimates, default=self.srtt))

        if loss_detection_method in ['timeout', 'both']:
            temp_list = list(self.packet_sent_times.items()).copy()
            for seq_num, t in temp_list:
                if time.time() - t > t0:
                    # print(f"Packet {seq_num} timed out, resending.")
                    packet = next(p for p in self.packets if p.seq_num == seq_num)
                    self.send_packet(packet)
                    self.receive_ack()
                    lost_packets_methods['timeout'].append(seq_num)

        if loss_detection_method in ['out_of_order', 'both']:
            missing_acks = [i for i in range(self.last_largest_acknowledged) if i not in self.acknowledged]
            for ack_num in missing_acks:
                # print(f"Detected out of order packet {ack_num}, resending.")
                packet = next(p for p in self.packets if p.seq_num == ack_num)
                self.send_packet(packet)
                self.receive_ack()
                lost_packets_methods['out_of_order'].append(ack_num)


        return lost_packets_methods

    def send_packet(self, packet):
        num = random.random()
        packet.sent_time = time.time()
        self.packet_sent_times[packet.seq_num] = packet.sent_time
        if num > self.loss_probability:
            # print(f"Sent packet {packet.seq_num}")
            self.server_socket.sendto(packet.serialize(), self.client_address)
        else:
            # print(f"Packet {packet.seq_num} lost during sending.")
            self.lost_packets.append(packet.seq_num)


    def receive_ack(self):
        self.server_socket.settimeout(self.timeout)
        try:
            ack_data, addr = self.server_socket.recvfrom(1024)
            if ack_data:
                try:
                    ack = Ack.deserialize(ack_data)
                except:
                    return
                print(f"Server received ACK for packet {ack.ack_num}")  # Add this print statement
                self.acknowledged.add(ack.ack_num)
                if ack.ack_num in self.packet_sent_times:
                    rtt = time.time() - self.packet_sent_times[ack.ack_num]
                    if self.srtt == 0:
                        self.srtt = rtt
                        self.rtt_var = rtt / 2
                    else:
                        alpha, beta = 0.5, 0.25
                        self.rtt_var = (1 - alpha) * self.rtt_var + alpha * abs(self.srtt - rtt)
                        self.srtt = (1 - beta) * self.srtt + beta * rtt
                    self.pto = self.srtt + 4 * self.rtt_var
                    self.rtt_estimates.append(rtt)
                    del self.packet_sent_times[ack.ack_num]
                    # print(f"Received ACK for packet {ack.ack_num}, RTT: {rtt:.6f} seconds")
                    self.last_largest_acknowledged = ack.ack_num
        except socket.timeout:
            # print("Timeout occurred while waiting for ACK.")
            print("", end = "")

    def run(self, loss_detection_method):


        self.data[0] = loss_detection_method

        print("Waiting for client...")
        self.client_address = None
        while self.client_address is None:
            _, self.client_address = self.server_socket.recvfrom(1024)
        print(f"Client address: {self.client_address}")

        start_time = time.time()
        for packet in self.packets:
            self.send_packet(packet)
            self.detect_lost_packets(start_time, loss_detection_method)

            # Receive and process ACKs from client
            self.receive_ack()

        ## checking there is no pending packets to ack
        self.check_all_sent(len(self.packets)-1)

        end_time = time.time()
        self.transfer_time = end_time - start_time
        print(f"Time taken to transfer the file with {loss_detection_method} method: {self.transfer_time:.6f} seconds")

        self.send_end_of_transfer()
        self.server_socket.close()
        print('connection closed from server')

    def check_all_sent(self, nb_packets):
        ## securing everything arrived
        missing_acks = [i for i in range(nb_packets) if i not in self.acknowledged]
        while len(missing_acks) != 0:
            for ack_num in missing_acks:
                packet = next(p for p in self.packets if p.seq_num == ack_num)
                self.send_packet(packet)
                self.receive_ack()

            missing_acks = [i for i in range(self.last_largest_acknowledged) if i not in self.acknowledged]

    def send_end_of_transfer(self):

        end_packet = Packet(0, b"###END###")  # Use a special sequence number or data
        self.server_socket.sendto(end_packet.serialize(), self.client_address)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for sending packets to a client.")
    parser.add_argument('-p','--loss_probability', type=float, default=0.0, help='Probability of packet loss (default: 0.0)')
    parser.add_argument('-m','--loss_detection_method', type=str, default='out_of_order', help='Method for detecting packet loss (default: "out_of_order")')
    parser.add_argument('-s','--file_size', type=int, default=4, help='Size of sent file (default: 10)')
    args = parser.parse_args()

    FILE_PATH = 'sent_file.txt'

    data_to_send = 0
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) / (1024 * 1024) == args.file_size:
        print('file found')
        with open(FILE_PATH, 'rb') as file:  # Open in 'rb' mode to read binary data
            data_to_send = file.read()
    else:
        print('generating file')
        data_to_send = generate_random_data(args.file_size)

    server = Server(loss_probability=args.loss_probability, host='localhost', port=5000)
    server.load_file(data_to_send)  # Load the generated random data
    server.run(args.loss_detection_method)  # Run the server