set(SDK_PATH "/Users/maanders1/siliconlabs/git_repos/gsdks/gsdk_4.4.3")
set(COPIED_SDK_PATH "gecko_sdk_4.4.3")

add_library(slc_federated_learning_over_usart OBJECT
    "../${COPIED_SDK_PATH}/hardware/board/src/sl_board_control_gpio.c"
    "../${COPIED_SDK_PATH}/hardware/board/src/sl_board_init.c"
    "../${COPIED_SDK_PATH}/hardware/driver/configuration_over_swo/src/sl_cos.c"
    "../${COPIED_SDK_PATH}/hardware/driver/mx25_flash_shutdown/src/sl_mx25_flash_shutdown_usart/sl_mx25_flash_shutdown.c"
    "../${COPIED_SDK_PATH}/platform/common/src/sl_assert.c"
    "../${COPIED_SDK_PATH}/platform/common/src/sl_string.c"
    "../${COPIED_SDK_PATH}/platform/common/src/sl_syscalls.c"
    "../${COPIED_SDK_PATH}/platform/common/toolchain/src/sl_memory.c"
    "../${COPIED_SDK_PATH}/platform/Device/SiliconLabs/EFR32MG24/Source/startup_efr32mg24.c"
    "../${COPIED_SDK_PATH}/platform/Device/SiliconLabs/EFR32MG24/Source/system_efr32mg24.c"
    "../${COPIED_SDK_PATH}/platform/driver/debug/src/sl_debug_swo.c"
    "../${COPIED_SDK_PATH}/platform/emdrv/dmadrv/src/dmadrv.c"
    "../${COPIED_SDK_PATH}/platform/emdrv/ustimer/src/ustimer.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_burtc.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_cmu.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_core.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_emu.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_gpio.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_ldma.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_msc.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_prs.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_system.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_timer.c"
    "../${COPIED_SDK_PATH}/platform/emlib/src/em_usart.c"
    "../${COPIED_SDK_PATH}/platform/peripheral/src/peripheral_sysrtc.c"
    "../${COPIED_SDK_PATH}/platform/service/device_init/src/sl_device_init_dcdc_s2.c"
    "../${COPIED_SDK_PATH}/platform/service/device_init/src/sl_device_init_emu_s2.c"
    "../${COPIED_SDK_PATH}/platform/service/device_init/src/sl_device_init_hfxo_s2.c"
    "../${COPIED_SDK_PATH}/platform/service/device_init/src/sl_device_init_lfxo_s2.c"
    "../${COPIED_SDK_PATH}/platform/service/device_init/src/sl_device_init_nvic.c"
    "../${COPIED_SDK_PATH}/platform/service/iostream/src/sl_iostream.c"
    "../${COPIED_SDK_PATH}/platform/service/iostream/src/sl_iostream_uart.c"
    "../${COPIED_SDK_PATH}/platform/service/iostream/src/sl_iostream_usart.c"
    "../${COPIED_SDK_PATH}/platform/service/sleeptimer/src/sl_sleeptimer.c"
    "../${COPIED_SDK_PATH}/platform/service/sleeptimer/src/sl_sleeptimer_hal_burtc.c"
    "../${COPIED_SDK_PATH}/platform/service/sleeptimer/src/sl_sleeptimer_hal_sysrtc.c"
    "../${COPIED_SDK_PATH}/platform/service/sleeptimer/src/sl_sleeptimer_hal_timer.c"
    "../${COPIED_SDK_PATH}/platform/service/system/src/sl_system_init.c"
    "../${COPIED_SDK_PATH}/platform/service/system/src/sl_system_process_action.c"
    "../${COPIED_SDK_PATH}/platform/service/udelay/src/sl_udelay.c"
    "../${COPIED_SDK_PATH}/platform/service/udelay/src/sl_udelay_armv6m_gcc.S"
    "../app.c"
    "../app_iostream_usart.c"
    "../autogen/sl_board_default_init.c"
    "../autogen/sl_device_init_clocks.c"
    "../autogen/sl_event_handler.c"
    "../autogen/sl_iostream_handles.c"
    "../autogen/sl_iostream_init_usart_instances.c"
    "../main.c"
)

target_include_directories(slc_federated_learning_over_usart PUBLIC
   "../config"
   "../autogen"
   "../."
    "../${COPIED_SDK_PATH}/platform/Device/SiliconLabs/EFR32MG24/Include"
    "../${COPIED_SDK_PATH}/platform/common/inc"
    "../${COPIED_SDK_PATH}/hardware/board/inc"
    "../${COPIED_SDK_PATH}/platform/CMSIS/Core/Include"
    "../${COPIED_SDK_PATH}/hardware/driver/configuration_over_swo/inc"
    "../${COPIED_SDK_PATH}/platform/driver/debug/inc"
    "../${COPIED_SDK_PATH}/platform/service/device_init/inc"
    "../${COPIED_SDK_PATH}/platform/emdrv/dmadrv/inc"
    "../${COPIED_SDK_PATH}/platform/emdrv/common/inc"
    "../${COPIED_SDK_PATH}/platform/emlib/inc"
    "../${COPIED_SDK_PATH}/platform/service/iostream/inc"
    "../${COPIED_SDK_PATH}/hardware/driver/mx25_flash_shutdown/inc/sl_mx25_flash_shutdown_usart"
    "../${COPIED_SDK_PATH}/platform/peripheral/inc"
    "../${COPIED_SDK_PATH}/platform/common/toolchain/inc"
    "../${COPIED_SDK_PATH}/platform/service/system/inc"
    "../${COPIED_SDK_PATH}/platform/service/sleeptimer/inc"
    "../${COPIED_SDK_PATH}/platform/service/udelay/inc"
    "../${COPIED_SDK_PATH}/platform/emdrv/ustimer/inc"
)

target_compile_definitions(slc_federated_learning_over_usart PUBLIC
    "DEBUG_EFM=1"
    "EFR32MG24B220F1536IM48=1"
    "SL_BOARD_NAME=\"BRD4187C\""
    "SL_BOARD_REV=\"A01\""
    "HARDWARE_BOARD_DEFAULT_RF_BAND_2400=1"
    "HARDWARE_BOARD_SUPPORTS_1_RF_BAND=1"
    "HARDWARE_BOARD_SUPPORTS_RF_BAND_2400=1"
    "HFXO_FREQ=39000000"
    "SL_COMPONENT_CATALOG_PRESENT=1"
)

target_link_libraries(slc_federated_learning_over_usart PUBLIC
    "-Wl,--start-group"
    "gcc"
    "c"
    "m"
    "nosys"
    "-Wl,--end-group"
)
target_compile_options(slc_federated_learning_over_usart PUBLIC
    $<$<COMPILE_LANGUAGE:C>:-mcpu=cortex-m33>
    $<$<COMPILE_LANGUAGE:C>:-mthumb>
    $<$<COMPILE_LANGUAGE:C>:-mfpu=fpv5-sp-d16>
    $<$<COMPILE_LANGUAGE:C>:-mfloat-abi=hard>
    $<$<COMPILE_LANGUAGE:C>:-Wall>
    $<$<COMPILE_LANGUAGE:C>:-Wextra>
    $<$<COMPILE_LANGUAGE:C>:-Os>
    $<$<COMPILE_LANGUAGE:C>:-fdata-sections>
    $<$<COMPILE_LANGUAGE:C>:-ffunction-sections>
    $<$<COMPILE_LANGUAGE:C>:-fomit-frame-pointer>
    "$<$<COMPILE_LANGUAGE:C>:SHELL:-imacros sl_gcc_preinclude.h>"
    $<$<COMPILE_LANGUAGE:C>:-mcmse>
    $<$<COMPILE_LANGUAGE:C>:--specs=nano.specs>
    $<$<COMPILE_LANGUAGE:C>:-g>
    $<$<COMPILE_LANGUAGE:CXX>:-mcpu=cortex-m33>
    $<$<COMPILE_LANGUAGE:CXX>:-mthumb>
    $<$<COMPILE_LANGUAGE:CXX>:-mfpu=fpv5-sp-d16>
    $<$<COMPILE_LANGUAGE:CXX>:-mfloat-abi=hard>
    $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
    $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
    $<$<COMPILE_LANGUAGE:CXX>:-Wall>
    $<$<COMPILE_LANGUAGE:CXX>:-Wextra>
    $<$<COMPILE_LANGUAGE:CXX>:-Os>
    $<$<COMPILE_LANGUAGE:CXX>:-fdata-sections>
    $<$<COMPILE_LANGUAGE:CXX>:-ffunction-sections>
    $<$<COMPILE_LANGUAGE:CXX>:-fomit-frame-pointer>
    "$<$<COMPILE_LANGUAGE:CXX>:SHELL:-imacros sl_gcc_preinclude.h>"
    $<$<COMPILE_LANGUAGE:CXX>:-mcmse>
    $<$<COMPILE_LANGUAGE:CXX>:--specs=nano.specs>
    $<$<COMPILE_LANGUAGE:CXX>:-g>
    $<$<COMPILE_LANGUAGE:ASM>:-mcpu=cortex-m33>
    $<$<COMPILE_LANGUAGE:ASM>:-mthumb>
    $<$<COMPILE_LANGUAGE:ASM>:-mfpu=fpv5-sp-d16>
    $<$<COMPILE_LANGUAGE:ASM>:-mfloat-abi=hard>
    "$<$<COMPILE_LANGUAGE:ASM>:SHELL:-imacros sl_gcc_preinclude.h>"
    "$<$<COMPILE_LANGUAGE:ASM>:SHELL:-x assembler-with-cpp>"
)

set(post_build_command )
set_property(TARGET slc_federated_learning_over_usart PROPERTY C_STANDARD 99)
set_property(TARGET slc_federated_learning_over_usart PROPERTY CXX_STANDARD 11)
set_property(TARGET slc_federated_learning_over_usart PROPERTY CXX_EXTENSIONS OFF)

target_link_options(slc_federated_learning_over_usart INTERFACE
    -mcpu=cortex-m33
    -mthumb
    -mfpu=fpv5-sp-d16
    -mfloat-abi=hard
    -T${CMAKE_CURRENT_LIST_DIR}/../autogen/linkerfile.ld
    --specs=nano.specs
    "SHELL:-Xlinker -Map=$<TARGET_FILE_DIR:federated_learning_over_usart>/federated_learning_over_usart.map"
    -Wl,--gc-sections
    -Wl,--no-warn-rwx-segments
)

# BEGIN_SIMPLICITY_STUDIO_METADATA=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END_SIMPLICITY_STUDIO_METADATA
