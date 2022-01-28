################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (9-2020-q2-update)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../OLED/Src/oled.c 

OBJS += \
./OLED/Src/oled.o 

C_DEPS += \
./OLED/Src/oled.d 


# Each subdirectory must supply rules for building sources it contributes
OLED/Src/%.o: ../OLED/Src/%.c OLED/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -DUSE_HAL_DRIVER -DSTM32F407xx -c -I"C:/Users/rhyss/STM32CubeIDE/workspace_1.8.0/CE3004 MDP/OLED/Inc" -I../Core/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../Drivers/CMSIS/Include -I../Middlewares/Third_Party/FreeRTOS/Source/include -I../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -Os -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-OLED-2f-Src

clean-OLED-2f-Src:
	-$(RM) ./OLED/Src/oled.d ./OLED/Src/oled.o

.PHONY: clean-OLED-2f-Src

