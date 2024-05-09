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

enum States {
    WAITING_FOR_PARAMS,
    TRAIN_MODEL,
    TRANSMIT_NEW_PARAMS,
    TRAINING_DONE,
};

struct state_machine {
    enum States state;
    enum States prev_state;
};

void new_params_to_host(void);

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
