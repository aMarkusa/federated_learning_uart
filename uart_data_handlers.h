#ifndef UART_DATA_HANDLERS
#define UART_DATA_HANDLERS

#include <stdint.h>

enum Command {
    GLOBAL_MODEL_PARAMETERS,
    LOCAL_MODEL_PARAMETERS,
    DATASET_X,
    DATASET_Y,
    ACK,
};

uint16_t training_data_handler(uint8_t* packet_data, uint8_t data_len, int16_t** training_data_array, uint8_t sequence_nr);
void model_parameters_handler(uint8_t* packet_data, uint8_t data_len, int16_t* model_parameters_array);
void convert_uint8_t_array_to_int16_t_array(uint8_t* input_array, uint8_t input_len, int16_t* output_array);

#endif /* UART_DATA_HANDLERS */
