/*
 * gpio_init.c
 *
 * Created: 2019-03-19 16:47:17
 *  Author: erikw_000
 */ 

#include "driver_init.h"
#include "gpio_init.h"

void gpio_init(void)
{
#ifdef INIT_GPIO
	gpio_set_pin_level(DGI_GPIO0, GPIO_LOW);
	gpio_set_pin_level(DGI_GPIO1, GPIO_LOW);
	gpio_set_pin_level(DGI_GPIO2, GPIO_LOW);
	gpio_set_pin_level(DGI_GPIO3, GPIO_LOW);

	// Set pin direction to output
	gpio_set_pin_direction(DGI_GPIO0, GPIO_DIRECTION_OUT);
	gpio_set_pin_direction(DGI_GPIO1, GPIO_DIRECTION_OUT);
	gpio_set_pin_direction(DGI_GPIO2, GPIO_DIRECTION_OUT);
	gpio_set_pin_direction(DGI_GPIO3, GPIO_DIRECTION_OUT);

	gpio_set_pin_function(DGI_GPIO0, GPIO_PIN_FUNCTION_OFF);
	gpio_set_pin_function(DGI_GPIO1, GPIO_PIN_FUNCTION_OFF);
	gpio_set_pin_function(DGI_GPIO2, GPIO_PIN_FUNCTION_OFF);
	gpio_set_pin_function(DGI_GPIO3, GPIO_PIN_FUNCTION_OFF);
#endif

#ifdef INIT_LED
	gpio_set_pin_level(LED0, LED_OFF);

	// Set pin direction to output
	gpio_set_pin_direction(LED0, GPIO_DIRECTION_OUT);

	gpio_set_pin_function(LED0, GPIO_PIN_FUNCTION_OFF);
#endif

	delay_ms(10);
}