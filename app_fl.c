#include <stdio.h>
#include <stdint.h>

#define LEARNING_RATE 0.0001
#define MAX_ITERATIONS 10000
#define TRAINING_LIMIT 3


// Function to calculate the mean squared error
float mean_squared_error(uint16_t* num_samples, float *w1, float *b, int16_t* inputs, int16_t* targets) {
    float error = 0;
    for (int i = 0; i < *num_samples; i++) {
        float prediction = *w1 * inputs[i] + *b;
        error += (targets[i] - prediction) * (targets[i] - prediction);
    }
    return error / (float)(*num_samples);
}

// Function to update parameters using gradient descent
void gradient_descent(uint16_t* num_samples, float *w1, float *b, int16_t* inputs, int16_t* targets) {
    float w1_gradient = 0, b_gradient = 0;
    for (int i = 0; i < *num_samples; i++) {
        float prediction = *w1 * inputs[i] + *b;
        w1_gradient += (targets[i] - prediction) * inputs[i];
        b_gradient += (targets[i] - prediction);
    }
    w1_gradient = w1_gradient * (-2/(float)(*num_samples));
    b_gradient = b_gradient * (-2/(float)(*num_samples));
    *w1 -= LEARNING_RATE * w1_gradient;
    *b -= LEARNING_RATE * b_gradient;
}

int train_model(uint16_t num_samples, float* w1, float* b, int16_t* inputs, int16_t* targets, float* lowest_mse) {
    float mse;
    float best_w1;
    float best_b;
    uint8_t consecutive_increases;
    for (int i = 0; i < MAX_ITERATIONS; i++) {
        gradient_descent(&num_samples, w1, b, inputs, targets);
        mse = mean_squared_error(&num_samples, w1, b, inputs, targets);
        if (mse < *lowest_mse || i == 0){
            *lowest_mse = mse;
            best_w1 = *w1;
            best_b = *b;
            consecutive_increases = 0;
        }
        else {
            consecutive_increases++;
            if (consecutive_increases >= TRAINING_LIMIT){
                *w1 = best_w1;
                *b = best_b;
                break;
            }
        }
    }

    return 0;
}
