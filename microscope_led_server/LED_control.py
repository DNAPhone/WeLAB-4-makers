import wiringpi
import logging


__author__ = 'DNAPhone S.r.l.'


logging.basicConfig()
log = logging.getLogger("logger")
log.setLevel(logging.DEBUG)


def change_led_status(status, led_value):

    if status == 'ON':

        log.debug("Turning led on to %d" % led_value)

        wiringpi.pinMode(18, 2)  # Setting GPIO pin 18 to PWM (0 is input, 1 is output and 2 is PWM, which only works for pin 18)
        wiringpi.pwmWrite(18, led_value)  # duty cycle is a value between 0 and 1024

    else:

        log.debug("Turning led off")

        wiringpi.pwmWrite(18, 0)  # Switch PWM output to 0
        wiringpi.pinMode(18, 0)  # Setting GPIO pin 18 to input
