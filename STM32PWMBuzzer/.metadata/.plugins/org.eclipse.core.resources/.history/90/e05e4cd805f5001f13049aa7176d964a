#include "LCD.h"
#include "stm32f1xx_hal.h"
#include "string.h"
#include "stdio.h"

void LCD_Enable(void) {
    HAL_GPIO_WritePin(E, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(E, GPIO_PIN_RESET);
    HAL_Delay(1);
}

void LCD_Command(uint8_t cmd) {
    HAL_GPIO_WritePin(RS, GPIO_PIN_RESET);  // Komut modu
    HAL_GPIO_WritePin(D4, (cmd >> 4) & 0x01);
    HAL_GPIO_WritePin(D5, (cmd >> 5) & 0x01);
    HAL_GPIO_WritePin(D6, (cmd >> 6) & 0x01);
    HAL_GPIO_WritePin(D7, (cmd >> 7) & 0x01);
    LCD_Enable();

    HAL_GPIO_WritePin(D4, cmd & 0x01);
    HAL_GPIO_WritePin(D5, (cmd >> 1) & 0x01);
    HAL_GPIO_WritePin(D6, (cmd >> 2) & 0x01);
    HAL_GPIO_WritePin(D7, (cmd >> 3) & 0x01);
    LCD_Enable();
}

void LCD_SendChar(char data) {
    HAL_GPIO_WritePin(RS, GPIO_PIN_SET);  // Veri modu
    HAL_GPIO_WritePin(D4, (data >> 4) & 0x01);
    HAL_GPIO_WritePin(D5, (data >> 5) & 0x01);
    HAL_GPIO_WritePin(D6, (data >> 6) & 0x01);
    HAL_GPIO_WritePin(D7, (data >> 7) & 0x01);
    LCD_Enable();

    HAL_GPIO_WritePin(D4, data & 0x01);
    HAL_GPIO_WritePin(D5, (data >> 1) & 0x01);
    HAL_GPIO_WritePin(D6, (data >> 2) & 0x01);
    HAL_GPIO_WritePin(D7, (data >> 3) & 0x01);
    LCD_Enable();
}

void LCD_SendString(char *str) {
    while (*str) {
        LCD_SendChar(*str++);
    }
}

void LCD_SetCursor(uint8_t row, uint8_t col) {
    uint8_t pos;
    if (row == 0) pos = 0x80 + col;
    else pos = 0xC0 + col;
    LCD_Command(pos);
}

void LCD_Init(void) {
    HAL_Delay(50);
    LCD_Command(0x33);
    LCD_Command(0x32);
    LCD_Command(0x28);
    LCD_Command(0x0C);
    LCD_Command(0x06);
    LCD_Command(0x01);
}
