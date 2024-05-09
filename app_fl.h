#ifndef APP_FL
#define APP_FL

float mean_squared_error(float* w1, float* b, float inputs[], float targets[]);

void gradient_descent(float *w1, float *b, float inputs[], float targets[]);

int train_model(uint16_t num_samples, float* w1, float* b, uint8_t* inputs, uint8_t* targets,
                float* lowest_mse);

#endif /* APP_FL */
