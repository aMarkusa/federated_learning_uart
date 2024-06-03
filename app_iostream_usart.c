/***************************************************************************/ /**
* @file
* @brief iostream usart examples functions
*******************************************************************************
* # License
* <b>Copyright 2020 Silicon Laboratories Inc. www.silabs.com</b>
*******************************************************************************
*
* The licensor of this software is Silicon Laboratories Inc. Your use of this
* software is governed by the terms of Silicon Labs Master Software License
* Agreement (MSLA) available at
* www.silabs.com/about-us/legal/master-software-license-agreement. This
* software is distributed to you in Source Code format and is governed by the
* sections of the MSLA applicable to Source Code.
*
* TODO: Think about error handling
******************************************************************************/
#include "app_iostream_usart.h"
#include "app_fl.h"
#include "em_chip.h"
#include "em_usart.h"
#include "sl_iostream.h"
#include "sl_iostream_handles.h"
#include "sl_iostream_init_instances.h"
#include "sl_iostream_usart.h"
#include "sl_iostream_usart_vcom_config.h"
#include "sl_sleeptimer.h"
#include "uart_data_handlers.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*******************************************************************************
 *******************************   DEFINES   ***********************************
 ******************************************************************************/

/* Finite state machine*/
struct StateMachine fsm;
struct TrainingData training_data;
uint8_t data_buffer[PACKET_DATA_BUFFER_SIZE];
float current_w = 0.0;
float current_b = 0.0;
float global_lowest_mse = 0;
float global_best_current_w;
float gloabl_best_b;
float lowest_mse;
bool model_parameters_received = false;

void app_iostream_usart_init(void) {
    sl_iostream_set_default(sl_iostream_vcom_handle);

    training_data.x_values = NULL;
    training_data.y_values = NULL;
    training_data.x_len = 0;
    training_data.y_len = 0;
}

void set_new_state(enum States new_state) {
    fsm.prev_state = fsm.state;
    fsm.state = new_state;
}

void fl_fsm(void) {
    switch (fsm.state) {
        case RECEIVE_DATA:
            app_iostream_usart_process_action();
            if (training_data.x_values != NULL && training_data.x_len == training_data.y_len && model_parameters_received) {
                set_new_state(TRAIN_MODEL);
            }
            break;
        case TRAIN_MODEL:
            lowest_mse = train_model(NUM_SAMPLES, &current_w, &current_b, training_data.x_values, training_data.y_values);
            set_new_state(SEND_DATA);
            break;
        case SEND_DATA:
            float parameters[3] = {current_w, current_b, lowest_mse};
            send_data((void *)parameters, 3, LOCAL_MODEL_PARAMETERS, 0);
            set_new_state(RECEIVE_DATA);
            break;
        default:
            break;
    }
}

void read_and_handle_uart_packet(uint8_t *data_buffer) {
    enum Command data_type = data_buffer[0];
    uint8_t data_len = data_buffer[1];
    uint8_t sequence_nr = data_buffer[2];

    switch (data_type) {
        case GLOBAL_MODEL_PARAMETERS:
        // TODO: Create a handler for this
            int16_t global_w = 0;
            int16_t global_b = 0;

            global_w = ((int16_t)data_buffer[3] << 8) | data_buffer[4];
            global_b = ((int16_t)data_buffer[5] << 8) | data_buffer[6];

            current_w = global_w / 100;
            current_b = global_b / 100;

            uint8_t ack_buffer[] = {0};
            send_data(ack_buffer, 1, ACK, 0);
            model_parameters_received = true;
            break;
        case DATASET_X:
            training_data.x_len = training_data_handler(data_buffer, data_len, &training_data.x_values, sequence_nr);
            break;
        case DATASET_Y:
            training_data.y_len = training_data_handler(data_buffer, data_len, &training_data.y_values, sequence_nr);
            break;
        default:
    }
}

void app_iostream_usart_process_action(void) {
    size_t bytes_read = 0;
    static uint8_t total_bytes_read = 0;
    static uint8_t last_byte = 0;
    sl_status_t status;
    uint8_t data_byte;
    static bool header_received = false;
    status = sl_iostream_read(sl_iostream_vcom_handle, &data_byte, 1, &bytes_read);

    if (bytes_read == 1 && status == SL_STATUS_OK) {
        data_buffer[total_bytes_read] = data_byte;
        total_bytes_read++;
        if (total_bytes_read == PACKET_HEADER_SIZE) {
            last_byte = PACKET_HEADER_SIZE + data_buffer[1];
            header_received = true;
        }
        if (header_received == true && total_bytes_read == last_byte) {
            read_and_handle_uart_packet(data_buffer);
            memset(data_buffer, 0, PACKET_DATA_BUFFER_SIZE);
            total_bytes_read = 0;
            header_received = false;
        }
#if LOCAL_ECHO
        /* Local echo */
        putchar(c);
#endif
    }
}

void send_data(void *data_buffer, uint8_t len, enum Command datatype, uint8_t sequence) {
    switch (datatype) {
        case LOCAL_MODEL_PARAMETERS: {
            float *buffer = (float *)data_buffer;
            int16_t trained_w = buffer[0] * 100; // Two decimals
            int16_t trained_b = buffer[1] * 100;
            int16_t lowest_mse_int = lowest_mse * 100;

            int8_t w_lsb = trained_w & 0xFF;
            int8_t w_msb = (trained_w >> 8) & 0xFF;
            int8_t b_lsb = trained_b & 0xFF;
            int8_t b_msb = (trained_b >> 8) & 0xFF;
            int8_t lowest_mse_lsb = lowest_mse_int & 0xFF;
            int8_t lowest_mse_msb = (lowest_mse_int >> 8) & 0xFF;

            int8_t tx_buffer[] = {datatype, len * 2, sequence, w_msb, w_lsb, b_msb, b_lsb, lowest_mse_msb, lowest_mse_lsb};
            sl_iostream_write(sl_iostream_vcom_handle, tx_buffer, sizeof(tx_buffer) / sizeof(uint8_t));
            break;
        }
        case ACK: {
            int8_t tx_buffer[] = {datatype, len, sequence, *(int8_t*)data_buffer};
            sl_iostream_write(sl_iostream_vcom_handle, tx_buffer, sizeof(tx_buffer) / sizeof(uint8_t));
        }
        default:
            break;
    }
}
