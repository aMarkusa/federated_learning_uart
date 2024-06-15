/***************************************************************************//**
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
 ******************************************************************************/

#ifndef APP_IOSTREAM_USART
#define APP_IOSTREAM_USART

#define LOCAL_ECHO 0
#ifndef BUFSIZE
#define BUFSIZE 80
#endif
#ifndef PACKET_HEADER_SIZE
#define PACKET_HEADER_SIZE 3
#endif
#ifndef PACKET_DATA_BUFFER_SIZE
#define PACKET_DATA_BUFFER_SIZE 256
#endif

#include <stdint.h>
#include "uart_data_handlers.h"

enum States {
    RECEIVE_DATA,
    TRAIN_MODEL,
    SEND_DATA,
    TRAINING_DONE,
};

struct StateMachine {
    enum States state;
    enum States prev_state;
};

struct TrainingData {
    int16_t* model_inputs;
    int16_t* model_targets;
    uint16_t x_len;
    uint16_t y_len;
};

void read_and_handle_uart_packet(uint8_t* header);

void send_data(void* data_buffer, uint8_t len, enum Command datatype, uint8_t sequence);

void set_new_state(enum States new_state);

/***************************************************************************//**
 * Finite state machine
 ******************************************************************************/
void fl_fsm(void);

/***************************************************************************//**
 * Initialize iostream usart
 ******************************************************************************/
void app_iostream_usart_init(void);

/***************************************************************************//**
 * iostream usart ticking function
 ******************************************************************************/
void app_iostream_usart_process_action(void);

#endif /* APP_IOSTREAM_USART */
