class Peripheral:
    def __init__(self, initial_training_params, nickname):
        self.nickname = nickname
        self._params = initial_training_params
        self._latest_rmse = None
        self._lowest_rmse = None
        self.final_rmse = None
        self._consecutive_rmse_increases = 0
        self._current_training_iteration = 1
        self._ready_to_receive = True
        self._timeout = 60
        self._active_training = False
        self._training_done = False
        self._dataset_len = None
        self._model_inputs = []
        self._model_targets = []

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params: list):
        self._params = params

    @property
    def latest_rmse(self):
        return self._latest_rmse

    @latest_rmse.setter
    def latest_rmse(self, rmse):
        self._latest_rmse = rmse
        if self.current_training_iteration == 1:
            self.lowest_rmse = rmse
        elif rmse < self.lowest_rmse:
            self.lowest_rmse = rmse
            self.consecutive_rmse_increases = 0
        else:
            self.consecutive_rmse_increases = self.consecutive_rmse_increases + 1

    @property
    def lowest_rmse(self):
        return self._lowest_rmse

    @lowest_rmse.setter
    def lowest_rmse(self, rmse):
        self._lowest_rmse = rmse

    @property
    def consecutive_rmse_increases(self):
        return self._consecutive_rmse_increases

    @consecutive_rmse_increases.setter
    def consecutive_rmse_increases(self, increases):
        self._consecutive_rmse_increases = increases

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

    @property
    def model_inputs(self):
        return self._model_inputs

    @model_inputs.setter
    def model_inputs(self, values):
        self._model_inputs = values

    @property
    def model_targets(self):
        return self._model_targets

    @model_targets.setter
    def model_targets(self, values):
        self._model_targets = values
