#include <atmel_start.h>

int main(void)
{
	/* Initializes MCU, drivers and middleware */
	atmel_start_init();

	/* Replace with your application code */
	while (1) {
		delay_ms(100);
		gpio_toggle_pin_level(DGI_GPIO0);
		delay_ms(100);
		gpio_toggle_pin_level(DGI_GPIO1);
		delay_ms(100);
		gpio_toggle_pin_level(DGI_GPIO2);
		delay_ms(100);
		gpio_set_pin_level(DGI_GPIO3, GPIO_HIGH);
		gpio_toggle_pin_level(LED0);
		delay_ms(10);
		gpio_set_pin_level(DGI_GPIO3, GPIO_LOW);
	}
}
