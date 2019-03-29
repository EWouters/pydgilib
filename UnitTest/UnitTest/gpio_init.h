/*
 * gpio_init.h
 *
 * Created: 2019-03-19 16:47:35
 *  Author: erikw_000
 */ 


#ifndef GPIO_INIT_H_
#define GPIO_INIT_H_

#define DELAY delay_ms(1)

#ifdef INIT_GPIO
#define GPIO_HIGH true
#define GPIO_LOW false

#define DGI_GPIO0 GPIO(GPIO_PORTA, 10)
#define DGI_GPIO1 GPIO(GPIO_PORTA, 11)
#define DGI_GPIO2 GPIO(GPIO_PORTA, 23)
#define DGI_GPIO3 GPIO(GPIO_PORTA, 27)

#define START_MEASURE(PIN) DELAY; gpio_set_pin_level(PIN, GPIO_HIGH)
#define STOP_MEASURE(PIN) gpio_set_pin_level(PIN, GPIO_LOW); DELAY
#define END_MEASUREMENT DELAY; gpio_set_pin_level(DGI_GPIO0, GPIO_HIGH); gpio_set_pin_level(DGI_GPIO1, GPIO_HIGH); gpio_set_pin_level(DGI_GPIO2, GPIO_HIGH); gpio_set_pin_level(DGI_GPIO3, GPIO_HIGH)

#endif

#ifdef INIT_LED

#define LED0 GPIO(GPIO_PORTA, 7)

#define LED_ON gpio_set_pin_level(LED0, false)
#define LED_OFF gpio_set_pin_level(LED0, true)

#endif

void gpio_init(void);

#endif /* GPIO_INIT_H_ */