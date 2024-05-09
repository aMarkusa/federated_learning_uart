#!/Users/maanders1/miniconda3/bin/python
from SerialInterface import SerialInterface
from time import sleep

MAX_ITERATIONS = 10000
MAX_MSE_INCREASES = 3
START_W = 1
START_B = 3
START_PARAMS = f"{START_W}:{START_B}"
parsed_data = []
consecutive_increases = 0

peripheral_port = '/dev/cu.usbmodem0004402930881'

def parse_response(response):
    parsed_data.clear()
    response = response.split(':')
    w = int(response[0]) / 100.0
    b = int(response[1]) / 100.0
    mse = int(response[2]) / 100.0
    
    parsed_data.append(w)
    parsed_data.append(b)
    parsed_data.append(mse)
     
    data = str(w) + ':' + str(b)
    return data
    
def continue_training(mse, iteration):
    global lowest_mse
    global consecutive_increases
    if iteration == 0:
        lowest_mse = mse
    elif mse < lowest_mse:
        lowest_mse = mse
        consecutive_increases = 0
    else:
        consecutive_increases = consecutive_increases + 1
        if consecutive_increases >= MAX_MSE_INCREASES:
            return False
    
    return True
            

if __name__ == "__main__":
    serial_interface = SerialInterface(port=peripheral_port, baud_rate=115200, rtscts=True)
    
    serial_interface.open_serial_connection()
    params = START_PARAMS
    print(f"Initial params - w: {START_W}, b: {START_B}")
    for i in range(MAX_ITERATIONS):
        print("Sending parameters to peripheral.\n")
        serial_interface.flush_input_buffer()
        serial_interface.write_data(data=params)
        sleep(0.1)
        new_params = serial_interface.wait_for_data(100)
        print(new_params)
        if len(new_params) != 0:
            params = parse_response(new_params)
            print(f"New parameters - w: {parsed_data[0]}, b: {parsed_data[1]}")
            print("MSE: ", parsed_data[2])
            if not continue_training(parsed_data[2], i):
                print("\n\n\nTraining finished after : ", i+1, " iterations.")
                print("w: ", parsed_data[0])
                print("b:", parsed_data[1])
                print("MSE: ", parsed_data[2])
                break
    
    serial_interface.kill_interface()       


        