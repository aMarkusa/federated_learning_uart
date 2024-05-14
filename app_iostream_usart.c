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
******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "em_chip.h"
#include "sl_iostream.h"
#include "sl_iostream_init_instances.h"
#include "sl_iostream_handles.h"
#include "app_iostream_usart.h"
#include "app_fl.h"
#include "sl_sleeptimer.h"

/*******************************************************************************
 *******************************   DEFINES   ***********************************
 ******************************************************************************/

#define LOCAL_ECHO 0
#ifndef BUFSIZE
#define BUFSIZE 80
#endif
#ifndef NUM_SAMPLES
#define NUM_SAMPLES 200
#endif
#ifndef PACKET_HEADER_LEN
#define PACKET_HEADER_LEN 3
#endif

/*******************************************************************************
 ***************************  LOCAL VARIABLES   ********************************
 ******************************************************************************/

/* Finite state machine*/
struct state_machine fsm;

float inputs[NUM_SAMPLES] = {21,94,8,96,57,29,43,27,23,57,92,95,37,46,85,6,90,83,58,23,61,5,70,40,75,57,66,79,2,36,16,79,31,15,40,9,0,95,68,29,12,66,72,84,56,79,72,18,66,93,50,57,22,4,9,65,2,23,56,44,47,0,49,94,22,80,86,21,22,13,73,92,78,36,33,89,47,55,3,83,63,30,53,53,2,13,18,62,70,21,29,14,76,73,73,9,44,48,5,0,30,21,51,61,91,11,98,68,62,68,25,89,42,27,87,38,29,93,41,72,56,19,2,86,31,48,98,70,87,36,82,10,82,19,17,5,4,63,50,60,2,92,81,15,18,5,47,0,85,84,34,6,99,46,88,32,12,28,66,70,95,68,76,17,37,58,71,2,43,36,24,73,34,91,54,47,68,89,36,11,6,14,74,96,86,50,24,18,88,0,27,77,72,6,53,33,62,26,3,82};
float targets[NUM_SAMPLES] = {30,192,0,214,122,74,78,65,37,135,194,190,80,75,170,42,182,171,125,51,119,9,176,86,141,125,134,181,4,56,25,159,73,4,70,34,-14,200,118,53,39,146,142,148,70,142,124,17,133,181,93,127,35,-8,26,121,51,65,115,91,83,8,119,186,35,148,172,62,18,42,161,179,164,77,83,166,101,117,18,170,127,61,118,98,23,30,31,127,150,62,86,20,160,162,142,18,64,116,39,-5,78,21,104,123,188,36,195,132,125,151,70,174,88,60,165,87,74,194,75,135,107,31,24,201,73,104,212,112,198,81,157,26,168,43,24,22,5,126,105,113,25,171,167,27,10,14,91,-23,179,192,60,9,214,85,181,37,22,78,165,145,193,135,142,22,72,120,137,-5,95,74,27,160,64,179,119,89,153,195,75,39,-2,16,164,187,152,92,49,16,165,-15,82,163,131,26,102,65,151,46,21,167};
float w1 = 0.0;
float b = 0.0;
float global_lowest_mse = 0;
float global_best_w1;
float gloabl_best_b;
float lowest_mse;
//enum Command command;

/*******************************************************************************
 **************************   GLOBAL FUNCTIONS   *******************************
 ******************************************************************************/

/***************************************************************************/ /**
                                                                               * Initialize example.
                                                                               ******************************************************************************/
void app_iostream_usart_init(void)
{
  /* Prevent buffering of output/input.*/
#if !defined(__CROSSWORKS_ARM) && defined(__GNUC__)
  //setvbuf(stdout, NULL, _IONBF, 0); /*Set unbuffered mode for stdout (newlib)*/
  //setvbuf(stdin, NULL, _IONBF, 0);  /*Set unbuffered mode for stdin (newlib)*/
#endif

  /* Setting default stream */
  sl_iostream_set_default(sl_iostream_vcom_handle);
}

void set_new_state(enum States new_state)
{
  fsm.prev_state = fsm.state;
  fsm.state = new_state;
}

void fl_fsm(void)
{
  switch (fsm.state)
  {
  case WAITING_FOR_PARAMS:
    app_iostream_usart_process_action();
    break;
  case TRAIN_MODEL:
    train_model(NUM_SAMPLES, &w1, &b, inputs, targets, &lowest_mse);
    set_new_state(TRANSMIT_NEW_PARAMS);
    break;
  case TRANSMIT_NEW_PARAMS:
    new_params_to_host();
    set_new_state(WAITING_FOR_PARAMS);
    break;
  default:
    break;
  }
}

void read_and_parse_uart_packet(uint8_t *header)
{
  uint8_t data_type = header[0];
  uint8_t data_len = header[1];
  uint8_t sequence = header[2];
  size_t bytes_read;
  
  uint8_t packet_data[4];

  sl_iostream_read(sl_iostream_vcom_handle, packet_data, data_len, &bytes_read);

  printf("%d, %d", packet_data[0], packet_data[1]);
}

void app_iostream_usart_process_action(void)
{
  int8_t c = 0;
  static uint8_t index = 0;
  sl_status_t status;
  uint8_t packet_header[PACKET_HEADER_LEN];
  size_t bytes_read;

  sl_sleeptimer_delay_millisecond(1);
  /* Retrieve characters, print local echo and full line back */
  status = sl_iostream_read(sl_iostream_vcom_handle, packet_header, 3, &bytes_read);
  
  if (bytes_read == PACKET_HEADER_LEN && status == SL_STATUS_OK)
  {
    read_and_parse_uart_packet(packet_header);
#if LOCAL_ECHO
      /* Local echo */
      putchar(c);
#endif
    }
  
}

void new_params_to_host()
{
  int16_t w1_int = (int)(w1 * 100);
  uint8_t w1_lsb = w1_int & 0xFF;
  uint8_t w1_msb = (w1_int >> 8) & 0xFF;
  int16_t b_int = (int)(b * 100);
  uint8_t b_lsb = b_int & 0xFF;
  uint8_t b_msb = (b_int >> 8) & 0xFF;
  int16_t lowest_mse_int = (int)(lowest_mse * 100);
  uint8_t lowest_mse_lsb = lowest_mse_int & 0xFF;
  uint8_t lowest_mse_msb = (lowest_mse_int >> 8) & 0xFF;

  uint8_t sequence = 0;
  uint8_t buffer[11] = {LOCAL_PARAMETERS, 6, sequence, w1_msb, w1_lsb, b_msb, b_lsb, lowest_mse_msb, lowest_mse_lsb};
  //printf("%d:%d:%u\r", w1_int, b_int, lowest_mse_int);
  sl_iostream_write(sl_iostream_vcom_handle, buffer, sizeof(buffer)/sizeof(uint8_t));
}
