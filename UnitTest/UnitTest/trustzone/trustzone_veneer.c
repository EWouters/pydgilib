/**
 * \file
 *
 * \brief TrustZone secure gateway veneer implementation.
 *
 * Copyright (c) 2018 Microchip Technology Inc. and its subsidiaries.
 *
 * \asf_license_start
 *
 * \page License
 *
 * Subject to your compliance with these terms, you may use Microchip
 * software and any derivatives exclusively with Microchip products.
 * It is your responsibility to comply with third party license terms applicable
 * to your use of third party software (including open source software) that
 * may accompany Microchip software.
 *
 * THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS".  NO WARRANTIES,
 * WHETHER EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE,
 * INCLUDING ANY IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY,
 * AND FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL MICROCHIP BE
 * LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, INCIDENTAL OR CONSEQUENTIAL
 * LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND WHATSOEVER RELATED TO THE
 * SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS BEEN ADVISED OF THE
 * POSSIBILITY OR THE DAMAGES ARE FORESEEABLE.  TO THE FULLEST EXTENT
 * ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN ANY WAY
 * RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
 * THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
 *
 * \asf_license_stop
 *
 */

#include "atmel_start.h"
#include "trustzone_veneer.h"
#include "trustzone_config.h"

/* ======== Non-secure callable common driver functions ======== */

/*
 * \brief Initialize peripheral clock.
 */
#if defined(__ICCARM__) /* IAR EWARM */
__cmse_nonsecure_entry int32_t nsc_periph_clock_init(uint32_t gclk_id, uint32_t gclk_src)
#else /* GCC, Keil MDK with ARM Compiler 6 */
int32_t __attribute__((cmse_nonsecure_entry)) nsc_periph_clock_init(uint32_t gclk_id, uint32_t gclk_src)
#endif
{
	if (hri_gclk_get_PCHCTRL_CHEN_bit(GCLK, gclk_id)) {
		return 1; /* Already enabled */
	} else {
		hri_gclk_write_PCHCTRL_reg(GCLK, gclk_id, gclk_src | (1 << GCLK_PCHCTRL_CHEN_Pos));
	}
	return 0;
}

/*
 * \brief Initialize non-secure external interrupt.
 */
#if defined(__ICCARM__) /* IAR EWARM */
__cmse_nonsecure_entry int32_t nsc_ext_irq_init(struct ext_irq_setting irq_setting)
#else /* GCC, Keil MDK with ARM Compiler 6 */
int32_t __attribute__((cmse_nonsecure_entry)) nsc_ext_irq_init(struct ext_irq_setting irq_setting)
#endif
{
	uint32_t i;
	uint32_t evctrl_val         = hri_eic_read_EVCTRL_reg(EIC_SEC);
	uint32_t asynch_val         = hri_eic_read_ASYNCH_reg(EIC_SEC);
	uint32_t debouncen_val      = hri_eic_read_DEBOUNCEN_reg(EIC_SEC);
	uint32_t config_val         = hri_eic_read_CONFIG_reg(EIC_SEC, 0);
	uint32_t nonsec_mask        = hri_eic_read_NONSEC_reg(EIC_SEC);
	uint32_t config_nonsec_mask = 0;

	/* Calculate external interrupt settings with non-secure part  */
	evctrl_val    = (evctrl_val & (~nonsec_mask)) | (irq_setting.evctrl & nonsec_mask);
	asynch_val    = (asynch_val & (~nonsec_mask)) | (irq_setting.asynch & nonsec_mask);
	debouncen_val = (debouncen_val & (~nonsec_mask)) | (irq_setting.debouncen & nonsec_mask);
	for (i = 0; i < 8; i++) {
		if (nonsec_mask & (1u << i)) {
			config_nonsec_mask |= (0xFu << (i * 4));
		}
	}
	config_val = (config_val & (~config_nonsec_mask)) | (irq_setting.config[0] & config_nonsec_mask);

	/* Disable EIC */
	hri_eic_clear_CTRLA_ENABLE_bit(EIC_SEC);
	hri_eic_wait_for_sync(EIC_SEC, EIC_SYNCBUSY_ENABLE);

	/* Update external interrupt settings */
	hri_eic_write_EVCTRL_reg(EIC_SEC, evctrl_val);
	hri_eic_write_ASYNCH_reg(EIC_SEC, asynch_val);
	hri_eic_write_DEBOUNCEN_reg(EIC_SEC, debouncen_val);
	hri_eic_write_CONFIG_reg(EIC_SEC, 0, config_val);

	/* Enable EIC */
	hri_eic_set_CTRLA_ENABLE_bit(EIC_SEC);

	return 0;
}

/* ======== Non-secure callable functions defined by customer ======== */
/*
 * You may add your secure gateway veneer functions in this file
 * and the function declaration into trustzone_veneer.h.
 */
