class Packet:
    def __init__(self, seq_num, data):
        self.seq_num = seq_num
        self.data = data

    def serialize(self):
        """Convert the Packet object to a bytes object for transmission."""
        seq_num_bytes = struct.pack('>I', self.seq_num)  # Pack the sequence number as an unsigned int
        data_len_bytes = struct.pack('>I', len(self.data))  # Pack the length of the data as an unsigned int
        return seq_num_bytes + data_len_bytes + self.data

    @classmethod
    def deserialize(cls, byte_data):
        """Convert a bytes object back into a Packet object."""
        seq_num = struct.unpack('>I', byte_data[:4])[0]  # Unpack the sequence number
        data_len = struct.unpack('>I', byte_data[4:8])[0]  # Unpack the length of the data
        data = byte_data[8:8+data_len]  # Extract the data
        return cls(seq_num, data)


import struct

class Ack:
    def __init__(self, ack_num, largest_acknowledged, ack_range, gap):
        self.ack_num = ack_num
        self.largest_acknowledged = largest_acknowledged
        self.ack_range = ack_range
        self.gap = gap

    def serialize(self):
        """Convert the Ack object to a bytes object for transmission."""
        return struct.pack('>IIII', self.ack_num, self.largest_acknowledged, self.ack_range, self.gap)

    @classmethod
    def deserialize(cls, byte_data):
        """Convert a bytes object back into an Ack object."""
        if len(byte_data) < 16:
            print(byte_data)
        ack_num, largest_acknowledged, ack_range, gap = struct.unpack('>IIII', byte_data[:16])
        return cls(ack_num, largest_acknowledged, ack_range, gap)


