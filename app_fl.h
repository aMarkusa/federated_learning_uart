#ifndef APP_FL
#define APP_FL

float mean_squared_error(float* w1, float* b, float inputs[], float targets[]);

void gradient_descent(float *w1, float *b, float inputs[], float targets[]);

float train_model(uint16_t num_samples, float* w1, float* b, int16_t* inputs, int16_t* targets, float* lowest_mse);

#endif /* APP_FL */
