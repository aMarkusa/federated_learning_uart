# Define minimal required version of CMake.
cmake_minimum_required(VERSION "3.25")

# Project definition
project(
	federated_learning_over_usart
	VERSION 1.0
	LANGUAGES C CXX ASM
)

# Include the definition of the slc_federated_learning_over_usart target,
# which contains the content of the SLC project
include(federated_learning_over_usart.cmake)

add_executable(federated_learning_over_usart
    # Add additional sources here
)

target_include_directories(federated_learning_over_usart PUBLIC
    # Add additional include paths here
)

target_compile_definitions(federated_learning_over_usart PUBLIC
    # Add additional macros here
)

target_compile_options(federated_learning_over_usart PUBLIC
    # Set additional compiler flags here
)

target_link_options(federated_learning_over_usart PUBLIC
    # Set additional linker flags here
)

# Link with the content defined in the SLC project
target_link_libraries(federated_learning_over_usart PRIVATE
    slc_federated_learning_over_usart
)

# Include managed project content if available
include(federated_learning_over_usart_project.cmake OPTIONAL RESULT_VARIABLE managed_project)
if(managed_project)
    message(STATUS "Using managed project content from ${managed_project}")
endif()

# Force the gcc linker command
set_target_properties(federated_learning_over_usart PROPERTIES LINKER_LANGUAGE C)

# Create .bin, .hex and .s37 artifacts after building the project
add_custom_command(TARGET federated_learning_over_usart
    POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O srec "$<TARGET_FILE:federated_learning_over_usart>" "$<TARGET_FILE_DIR:federated_learning_over_usart>/$<TARGET_FILE_BASE_NAME:federated_learning_over_usart>.s37"
    COMMAND ${CMAKE_OBJCOPY} -O ihex "$<TARGET_FILE:federated_learning_over_usart>" "$<TARGET_FILE_DIR:federated_learning_over_usart>/$<TARGET_FILE_BASE_NAME:federated_learning_over_usart>.hex"
    COMMAND ${CMAKE_OBJCOPY} -O binary "$<TARGET_FILE:federated_learning_over_usart>" "$<TARGET_FILE_DIR:federated_learning_over_usart>/$<TARGET_FILE_BASE_NAME:federated_learning_over_usart>.bin" 
)

# Run post-build pipeline to perform additional post-processing
if(post_build_command)
add_custom_command(TARGET federated_learning_over_usart
    POST_BUILD
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/..
    COMMAND ${post_build_command}
)
endif()