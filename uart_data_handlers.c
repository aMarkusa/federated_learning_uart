#include "uart_data_handlers.h"
#include "app_iostream_usart.h"
#include <stdlib.h>


void training_data_handler(uint8_t* packet_data, uint8_t data_len, int16_t** training_data_array, uint8_t sequence_nr){
  static uint8_t previous_sequence_nr = 0;
  static uint16_t total_sequence_bytes = 0;  // How long is the received sequence so far
  static uint8_t total_packets_received = 0;  // How many packets have been received, including discarded packets
  static uint8_t consecutive_lost_packets = 0;
  static uint16_t append_start_pointer = 0;
  int16_t* tmp = NULL;

  if (sequence_nr == (previous_sequence_nr + 1)){
    total_sequence_bytes += data_len;
    tmp = realloc(*training_data_array, total_sequence_bytes);
    if (tmp == NULL){
      // Do something
    }
    else {
      *training_data_array = tmp;
    }
    previous_sequence_nr = sequence_nr;
    convert_uint8_t_array_to_int16_t_array(packet_data + PACKET_HEADER_SIZE, data_len, *training_data_array + (append_start_pointer));
    append_start_pointer = total_sequence_bytes / 2;
    consecutive_lost_packets = 0;
  }
  else if (sequence_nr == 255){
    if (consecutive_lost_packets == 0){
        previous_sequence_nr = sequence_nr;
        training_data_array = realloc(training_data_array, total_sequence_bytes);
        if (training_data_array == NULL){
          // do something
        }
        convert_uint8_t_array_to_int16_t_array(packet_data + PACKET_HEADER_SIZE, data_len, *training_data_array + (append_start_pointer));
        append_start_pointer = total_sequence_bytes - 1;
      }
  }
  else {
    consecutive_lost_packets++;
  }

  total_packets_received++;
  uint8_t ack_buffer[] = {previous_sequence_nr};
  send_data(ack_buffer, 1, ACK, 0); 
}

void convert_uint8_t_array_to_int16_t_array(uint8_t* input_array, uint8_t input_len, int16_t* output_array){
  uint8_t num_pairs = input_len / 2;  // We have pairs of int8_t that form one int16_t

  for (uint8_t i = 0; i < num_pairs; i++){
    output_array[i] = ((int16_t)input_array[2 * i] << 8) | (int16_t)input_array[2 * i + 1];
  }
}