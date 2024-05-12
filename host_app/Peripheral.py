class Peripheral():
    def __init__(self, initial_training_params):
        self._params = initial_training_params
        self._latest_mse = 0
        self._lowest_mse = 0
        self._consecutive_mse_increases = 0
        self._current_training_iteration = 0
        self._ready_to_receive = True
        self._timeout = 60
        self._active_training = False
        self._training_done = False
        self._dataset_len = 100
        
    @property
    def params(self):
        return self._params
    
    @params.setter
    def params(self, params: list):
        self._params = params
        
    @property
    def latest_mse(self):
        return self._latest_mse
    
    @latest_mse.setter
    def latest_mse(self, mse):
        self._latest_mse = mse
        if self.current_training_iteration == 0:
            self.lowest_mse = mse
        elif mse < self.lowest_mse:
            self.lowest_mse = mse
            self.consecutive_mse_increases = 0
        else:
            self.consecutive_mse_increases = self.consecutive_mse_increases + 1
        
    @property
    def lowest_mse(self):
        return self._lowest_mse
    
    @lowest_mse.setter
    def lowest_mse(self, mse):
        self._lowest_mse = mse
        
    @property
    def consecutive_mse_increases(self):
        return self._consecutive_mse_increases
    
    @consecutive_mse_increases.setter
    def consecutive_mse_increases(self, increases):
        self._consecutive_mse_increases = increases
        
    @property
    def current_training_iteration(self):
        return self._current_training_iteration
    
    @current_training_iteration.setter
    def current_training_iteration(self, iteration):
        self._current_training_iteration = iteration
    
    @property
    def ready_to_receive(self):
        return self._ready_to_receive
    
    @ready_to_receive.setter
    def ready_to_receive(self, ready: bool):
        self._ready_to_receive = ready
        
    @property 
    def timeout(self):
        return self._timeout
    
    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout
        
    @property
    def active_training(self):
        return self._active_training
    
    @active_training.setter
    def active_training(self, training: bool):
        self._active_training = training
    
    @property
    def dataset_len(self):
        return self._dataset_len
    
    @dataset_len.setter
    def dataset_len(self, len):
        self._dataset_len = len
        
    @property
    def training_done(self):
        return self._training_done
    
    @training_done.setter
    def training_done(self, done: bool):
        self._training_done = done