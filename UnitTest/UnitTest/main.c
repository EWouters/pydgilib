#include <atmel_start.h>

int main(void)
{
	/* Initializes MCU, drivers and middleware */
	atmel_start_init();

	/* Replace with your application code */
	for (uint8_t i = 0; i < 10; i++) {
		delay_ms(100);
		START_MEASURE(DGI_GPIO0);
		delay_ms(10);
		STOP_MEASURE(DGI_GPIO0);
		START_MEASURE(DGI_GPIO1);
		delay_ms(20);
		STOP_MEASURE(DGI_GPIO1);
		START_MEASURE(DGI_GPIO2);
		delay_ms(30);
		STOP_MEASURE(DGI_GPIO2);
		START_MEASURE(DGI_GPIO3);
		gpio_toggle_pin_level(LED0);
		delay_ms(40);
		STOP_MEASURE(DGI_GPIO3);
	}
	END_MEASUREMENT;
}
