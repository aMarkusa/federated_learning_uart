import serial
class SerialInterface():
    def __init__(self, port=None, baud_rate=115200, rtscts=True):
        self._port = port
        self._baud_rate=baud_rate
        self._rtscts = rtscts
        self._connection = None
        
    def open_serial_connection(self):
        try:
            self._connection = serial.Serial(self._port, self._baud_rate, rtscts=self._rtscts)
            print("Connection established to " + self._port)
        except Exception as e:
            print(e)
            exit()
            
    def write_data(self, data: str):
        data = data + '\r'
        data = bytes(data, 'utf-8')
        try:
            self._connection.write(data)
        except Exception as e:
            print(e)

    def wait_for_data(self, timeout) -> str: 
        self._connection.timeout = timeout
        data = self._connection.read_until(b'\r').decode('utf-8')
        return data
    
    def flush_input_buffer(self):
        self._connection.reset_input_buffer()
        
    def kill_interface(self):
        self._connection.close()
            
        
    