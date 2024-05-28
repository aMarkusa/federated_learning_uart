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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "em_chip.h"
#include "sl_iostream.h"
#include "sl_iostream_init_instances.h"
#include "sl_iostream_handles.h"
#include "app_iostream_usart.h"
#include "sl_iostream_usart.h"
#include "app_fl.h"
#include "sl_sleeptimer.h"
#include "uart_data_handlers.h"
#include "em_usart.h"
#include "sl_iostream_usart_vcom_config.h"

/*******************************************************************************
 *******************************   DEFINES   ***********************************
 ******************************************************************************/

/* Finite state machine*/
struct state_machine fsm;
uint8_t data_buffer[PACKET_DATA_BUFFER_SIZE];
//float inputs[NUM_SAMPLES] = {21,94,8,96,57,29,43,27,23,57,92,95,37,46,85,6,90,83,58,23,61,5,70,40,75,57,66,79,2,36,16,79,31,15,40,9,0,95,68,29,12,66,72,84,56,79,72,18,66,93,50,57,22,4,9,65,2,23,56,44,47,0,49,94,22,80,86,21,22,13,73,92,78,36,33,89,47,55,3,83,63,30,53,53,2,13,18,62,70,21,29,14,76,73,73,9,44,48,5,0,30,21,51,61,91,11,98,68,62,68,25,89,42,27,87,38,29,93,41,72,56,19,2,86,31,48,98,70,87,36,82,10,82,19,17,5,4,63,50,60,2,92,81,15,18,5,47,0,85,84,34,6,99,46,88,32,12,28,66,70,95,68,76,17,37,58,71,2,43,36,24,73,34,91,54,47,68,89,36,11,6,14,74,96,86,50,24,18,88,0,27,77,72,6,53,33,62,26,3,82};
//float targets[NUM_SAMPLES] = {30,192,0,214,122,74,78,65,37,135,194,190,80,75,170,42,182,171,125,51,119,9,176,86,141,125,134,181,4,56,25,159,73,4,70,34,-14,200,118,53,39,146,142,148,70,142,124,17,133,181,93,127,35,-8,26,121,51,65,115,91,83,8,119,186,35,148,172,62,18,42,161,179,164,77,83,166,101,117,18,170,127,61,118,98,23,30,31,127,150,62,86,20,160,162,142,18,64,116,39,-5,78,21,104,123,188,36,195,132,125,151,70,174,88,60,165,87,74,194,75,135,107,31,24,201,73,104,212,112,198,81,157,26,168,43,24,22,5,126,105,113,25,171,167,27,10,14,91,-23,179,192,60,9,214,85,181,37,22,78,165,145,193,135,142,22,72,120,137,-5,95,74,27,160,64,179,119,89,153,195,75,39,-2,16,164,187,152,92,49,16,165,-15,82,163,131,26,102,65,151,46,21,167};
float current_w = 0.0;
float current_b = 0.0;
float global_lowest_mse = 0;
float global_best_current_w;
float gloabl_best_b;
float lowest_mse;
//enum Command command;

void app_iostream_usart_init(void)
{
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
    case RECEIVE_DATA:
      app_iostream_usart_process_action();
      break;
    case TRAIN_MODEL:
      //train_model(NUM_SAMPLES, &current_w, &current_b, x_values, y_values, &lowest_mse);
      set_new_state(SEND_DATA);
      break;
    case SEND_DATA:
      float parameters[3] = {current_w, current_b, lowest_mse};
      send_data((void*)parameters, 3, LOCAL_PARAMETERS, 0);
      set_new_state(RECEIVE_DATA);
      break;
    default:
      break;
  }
}

void read_and_handle_uart_packet(uint8_t* data_buffer)
{
  static int16_t* x_values = NULL;
  static int16_t* y_values = NULL;
  enum Command data_type = data_buffer[0];
  uint8_t data_len = data_buffer[1];
  uint8_t sequence_nr = data_buffer[2];

  switch (data_type)
  {
    case GLOBAL_PARAMETERS:
      int16_t global_w = 0;
      int16_t global_b = 0;

      global_w = (global_w & data_buffer[0]) << 8;
      global_w = global_w & data_buffer[1];

      global_b = (global_b & data_buffer[2]) << 8;
      global_b = global_b & data_buffer[3];

      current_w = global_w / 100;
      current_b = global_b / 100;

      set_new_state(TRAIN_MODEL);
      break;
    case DATASET_X:
      training_data_handler(data_buffer, data_len, &x_values, sequence_nr);
      break;
    case DATASET_Y:
      training_data_handler(data_buffer, data_len, &y_values, sequence_nr);
      break;    
    default:
  }
}

void app_iostream_usart_process_action(void)
{
  size_t bytes_read = 0;
  static uint8_t total_bytes_read = 0;
  static uint8_t last_byte = 0;
  sl_status_t status;
  uint8_t data_byte;
  static bool header_received = false;
 
  //sl_sleeptimer_delay_millisecond(100);
  /* Retrieve characters, print local echo and full line back */
  status = sl_iostream_read(sl_iostream_vcom_handle, &data_byte, 1, &bytes_read);
  
  if (bytes_read == 1 && status == SL_STATUS_OK)
  {
    data_buffer[total_bytes_read] = data_byte;
    total_bytes_read++;
    if (total_bytes_read == PACKET_HEADER_SIZE){
      last_byte = PACKET_HEADER_SIZE + data_buffer[1];
      header_received = true;
    }
    if (header_received == true && total_bytes_read == last_byte){
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

void send_data(void* data_buffer, uint8_t len, enum Command datatype, uint8_t sequence)
{
  switch (datatype)
  {
    case LOCAL_PARAMETERS:
    {
      float* buffer = (float*)data_buffer;
      int16_t trained_w = buffer[0] * 100;  // Two decimals
      int16_t trained_b = buffer[1] * 100;
      int16_t lowest_mse_int = lowest_mse * 100;

      int8_t w_lsb = trained_w & 0xFF;
      int8_t w_msb = (trained_w >> 8) & 0xFF;
      int8_t b_lsb = trained_b & 0xFF;
      int8_t b_msb = (trained_b >> 8) & 0xFF;
      int8_t lowest_mse_lsb = lowest_mse_int & 0xFF;
      int8_t lowest_mse_msb = (lowest_mse_int >> 8) & 0xFF;

      int8_t tx_buffer[] = {datatype, len*2, sequence, w_msb, w_lsb, b_msb, b_lsb, lowest_mse_msb, lowest_mse_lsb};
      sl_iostream_write(sl_iostream_vcom_handle, tx_buffer, sizeof(tx_buffer)/sizeof(uint8_t));
      break;
    }
    case ACK:
    {
      int8_t tx_buffer[] = {datatype, len, sequence, *(int8_t*)data_buffer};
      sl_iostream_write(sl_iostream_vcom_handle, tx_buffer, sizeof(tx_buffer)/sizeof(uint8_t));
    }
    default:
    break;
  }

}
