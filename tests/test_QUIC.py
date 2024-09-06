import unittest
import time
import os
import signal
import sys
sys.path.append("..")
import tools
sys.path.append("/Tests")

TIMEOUT = 40

def parse_time():
    with open('server_output.txt', 'r') as file:
        for line in file:
            if "Time taken to transfer the file" in line:
                return float(line.split(" ")[-2].strip())

def run_simulation(timeout):
    print('Running with default parameters')
    signal.alarm(timeout)
    os.system('./RunSimulationDefault.sh')
    return parse_time()

def run_simulation_parameters(timeout, prob, method):
    print('Running with set parameters')
    signal.alarm(timeout)
    os.system(f'./RunSimulationParameters.sh {prob} {method} 10')
    return parse_time()

class TestQUIC(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        tools.generate_random_data(10)
    
    def test_single_run(self):
        try:
            time_taken = run_simulation(TIMEOUT)
            print(f'{time_taken}')
            time.sleep(0.001)
        except:
            self.fail('Run failed')
        print('Single run: passed')
    
    def test_multiple_runs(self):
        for _ in range(5):
            time.sleep(0.01)
            run_simulation(TIMEOUT)
            time.sleep(0.01)
        print('Multiple runs: passed')

    def test_probabilities_and_methods(self):
    
        for prob in [0, 0.01, 0.05, 0.1, 0.2]:
            try:
                time_taken = run_simulation_parameters(TIMEOUT,prob,'out_of_order')
                print(f'{time_taken}')
            except:
                self.fail('Run failed')

            try:
                time_taken = run_simulation_parameters(TIMEOUT,prob,'timeout')
                print(f'{time_taken}')
            except:
                self.fail('Run failed')
            
            try:
                time_taken = run_simulation_parameters(TIMEOUT,prob,'both')
                print(f'{time_taken}')
            except:
                self.fail('Run failed')
        print('probabilities and methods: passed')



if __name__ == '__main__':
    unittest.main()