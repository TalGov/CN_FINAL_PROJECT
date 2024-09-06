import random
import socket
import struct
import time

from classes import Packet, Ack

class Client:
    def __init__(self, server_ip='localhost', server_port=5000):
        self.received_packets = {}
        self.unacknowledged_packets = []

        # Client socket setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (server_ip, server_port)
        print(f"Connected to server at {server_ip}:{server_port}")

    def receive_packet(self):
        try:
            while True:
                # First, receive the header (8 bytes: 4 for seq_num + 4 for data_len)
                packet_data, server_addr = self.client_socket.recvfrom(1024*1024)
                if not packet_data:
                    break

                # Unpack the header
                header = packet_data[:8]
                seq_num = struct.unpack('>I', header[:4])[0]
                data_len = struct.unpack('>I', header[4:])[0]
                data = packet_data[8:]

                # print(type(Packet(seq_num, data).data))

                if len(data) != data_len:
                    print("Error: Received data length does not match the expected length.")
                    break

                if data == b'###END###':
                    print("End of file transfer detected.")
                    break

                # Deserialize the packet
                packet = Packet(seq_num, data)
                # print(f"Received packet {seq_num}")
                self.received_packets[seq_num] = packet
                self.send_ack(packet, server_addr)
        except Exception as e:
            print(f"Error receiving packet: {e}")
        finally:
            self.client_socket.close()
            print('connection closed from client')

    def send_ack(self, packet, server_addr):
        largest_acknowledged = max(self.received_packets.keys(), default=-1)
        ack_range = 0
        gap = 0

        for i in range(largest_acknowledged, -1, -1):
            if i in self.received_packets:
                ack_range += 1
            else:
                gap += 1
                break

        ack = Ack(packet.seq_num, largest_acknowledged, ack_range, gap)
        print(f"Sending ACK for packet {packet.seq_num}")
        time.sleep(random.random()*random.random()*0.02) # simulating dynamic network latency
        self.client_socket.sendto(ack.serialize(), server_addr)

    # def save_file(self, output_path):
    #     with open(output_path, 'wb') as f:
    #         for seq_num in sorted(self.received_packets):
    #             f.write(self.received_packets[seq_num].data)
    #     print(f"File saved to {output_path}")


if __name__ == "__main__":
    client = Client(server_ip='localhost', server_port=5000)
    connection_packet = Packet(0, b'\x00' * 16)
    client.client_socket.sendto(connection_packet.serialize(), client.server_address)
    client.receive_packet()
    
