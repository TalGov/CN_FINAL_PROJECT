import random
import argparse
import matplotlib.pyplot as plt

def generate_random_data(size):
    random_data = bytes(random.getrandbits(8) for _ in range(size*1024**2))
    with open('sent_file.txt','wb') as file:
        file.write(random_data)
    return random_data

def plot_data(data: dict):
    ratio = 3
    _, axis = plt.subplots(3, 4, figsize=(4*ratio, 3*ratio))


    i = 0
    j = 0
    for p in data.keys():
        for entry in data[p]:
            axis[i, j % 4].plot(entry[1][2], entry[1][1], label=entry[0])
            axis[i, j % 4].set_title("Loss = " + str(p))
            axis[i, j % 4].set_xlabel("Time")
            axis[i, j % 4].set_ylabel("#Sent Packets")
            axis[i, j % 4].legend()

        j += 1
        if j % 4 == 0 and j > 0:
            i += 1

    axis[2, 3].axis('off')
    plt.tight_layout()
    plt.show()
