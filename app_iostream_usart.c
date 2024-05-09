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

/*******************************************************************************
 *******************************   DEFINES   ***********************************
 ******************************************************************************/

#define LOCAL_ECHO 0
#ifndef BUFSIZE
#define BUFSIZE 80
#endif
#ifndef NUM_SAMPLES
#define NUM_SAMPLES 100
#endif

/*******************************************************************************
 ***************************  LOCAL VARIABLES   ********************************
 ******************************************************************************/

/* Input buffer */
static char buffer[BUFSIZE];

/* Finite state machine*/
struct state_machine fsm;

uint8_t inputs[NUM_SAMPLES] = {4,33,69,0,11,27,65,44,4,99,28,26,31,48,62,74,3,18,46,86,34,45,0,68,87,63,47,20,81,65,86,23,74,9,84,20,79,65,93,13,27,75,18,36,85,35,61,91,40,0,54,74,5,99,84,86,81,45,50,80,71,29,18,71,67,87,31,40,26,44,31,57,53,93,29,63,99,52,17,61,17,51,20,7,78,64,21,65,74,91,91,36,47,42,38,9,99,25,97,2};
uint8_t targets[NUM_SAMPLES] = {6,18,36,5,5,16,33,25,6,54,15,15,20,23,31,40,0,13,27,48,19,25,8,37,48,35,27,13,46,37,46,13,39,8,42,13,43,34,50,9,14,39,11,20,45,22,34,47,22,2,29,39,4,49,45,49,46,23,31,46,40,17,14,40,32,46,16,20,13,23,15,34,28,47,16,32,55,26,14,34,12,26,13,8,42,35,11,34,37,46,49,21,24,24,22,9,55,13,49,2};
float w1 = 0.0;
float b = 0.0;
float global_lowest_mse = 0;
float global_best_w1;
float gloabl_best_b;
float lowest_mse;

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
  setvbuf(stdout, NULL, _IONBF, 0); /*Set unbuffered mode for stdout (newlib)*/
  setvbuf(stdin, NULL, _IONBF, 0);  /*Set unbuffered mode for stdin (newlib)*/
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

void extract_parameters(char *buffer, size_t len)
{
  w1 = atof(buffer);
  for (uint8_t i = 0; i < len; i++)
  {
    if (buffer[i] == '\0')
    {
      b = atof(&buffer[i + 1]);
      break;
    }
  }
}

/***************************************************************************/ /**
                                                                               * Example ticking function.
                                                                               ******************************************************************************/

void app_iostream_usart_process_action(void)
{
  int8_t c = 0;
  static uint8_t index = 0;

  /* Retrieve characters, print local echo and full line back */
  c = getchar();
  if (c > 0)
  {
    if (c == ':')
    {
      buffer[index] = '\0';
      index++;
    }
    else if (c == '\r')
    {
      buffer[index] = '\0';
      extract_parameters(buffer, sizeof(buffer) / sizeof(char));
      set_new_state(TRAIN_MODEL);
      index = 0;
    }
    else
    {
      if (index < BUFSIZE - 1)
      {
        buffer[index] = c;
        index++;
      }
#if LOCAL_ECHO
      /* Local echo */
      putchar(c);
#endif
    }
  }
}

void new_params_to_host()
{
  uint16_t w1_int = (int)(w1 * 100);
  uint16_t b_int = (int)(b * 100);
  uint16_t lowest_mse_int = (int)(lowest_mse * 100);
  printf("%u:%u:%u\r\n", w1_int, b_int, lowest_mse_int);
}
