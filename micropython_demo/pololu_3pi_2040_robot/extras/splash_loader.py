def splash_loader(*, default_program, splash_delay_s, run_file_delay_ms):
    from pololu_3pi_2040_robot.display import Display
    display = Display()
    splash = None
    if splash_delay_s:
        # Display the splash screen ASAP.
        splash = display.load_pbm("pololu_3pi_2040_robot/extras/splash.pbm")
        display.blit(splash, 0, 0)
        display.show()

    welcome_song = "O5 e64a64 O6 msl32 d v12 d v10 d v8 d v6 d16"
    button_a_beep = "!c32"
    button_b_beep = "!e32"
    button_c_beep = "!g32"

    from pololu_3pi_2040_robot.buttons import ButtonA, ButtonB, ButtonC
    from pololu_3pi_2040_robot.buzzer import Buzzer
    from pololu_3pi_2040_robot.battery import Battery
    from pololu_3pi_2040_robot.rgb_leds import RGBLEDs
    from pololu_3pi_2040_robot.yellow_led import YellowLED
    import time
    from machine import PWM

    button_a = ButtonA()
    button_b = ButtonB()
    button_c = ButtonC()
    battery = Battery()
    buzzer = Buzzer() # turns off buzzer
    rgb_leds = RGBLEDs() # turns off RGB LEDs
    rgb_leds.set_brightness(4)

    # Initialize a PWM on the yellow LED at 0% duty cycle, which
    # corresponds to full brightness.  We can't initialize PWM with
    # the LED off so we'll just have it on for a while.
    pwm = PWM(YellowLED().pin)
    pwm.freq(1000)
    pwm.duty_u16(0)

    def del_vars():
        nonlocal display, splash, button_a, button_b, button_c, battery
        nonlocal buzzer, rgb_leds, pwm

        pwm.deinit()
        YellowLED() # turn off yellow LED and reset to an output

        del display, splash, button_a, button_b, button_c, battery
        del buzzer, rgb_leds, pwm

    def read_button():
        if button_a.is_pressed(): return "A"
        if button_b.is_pressed(): return "B"
        if button_c.is_pressed(): return "C"
        return None

    def initial_screen():
        start = time.ticks_ms()
        while True:
            if button_a.is_pressed():
                buzzer.play_in_background(button_a_beep)
                return "A"
            if button_b.is_pressed():
                buzzer.play_in_background(button_b_beep)
                return "B"
            if button_c.is_pressed():
                buzzer.play_in_background(button_c_beep)
                return "C"

            elapsed = time.ticks_ms() - start
            countdown_s = splash_delay_s - elapsed//1000
            if countdown_s <= 0:
                break

            display.fill(0)
            if elapsed < 1000:
                offset = 0
            else:
                offset = max(-32, -32 * (elapsed - 1000) // 400)
            display.blit(splash, 0, offset)
            display.text('Push C for menu', 0, 68+offset)
            display.text(f"Default ({countdown_s}s):", 0, 78+offset)

            if default_program:
                display.text(f"{default_program:>16}", 0, 88+offset)
            else:
                display.text('      menu', 0, 88+offset)

            display.show()

            led_period = 80
            decay = 500
            q = elapsed // led_period
            h = max(0, 240 - 240 * elapsed // 400)
            s = min(255, 220 + 35 * elapsed // 200)
            for i in range(4):
                if q >= i:
                    v = max(0, 255 - 255 * (elapsed - i * led_period) // decay)
                    rgb_leds.set_hsv(4-i, [h, s, v])
                    rgb_leds.set_hsv((4+i)%6, [h, s, v])
                else:
                    rgb_leds.set(4-i, [0, 0, 0])
                    rgb_leds.set((4+i)%6, [0, 0, 0])
            rgb_leds.show()

        return None

    def run_file(filename):
        rgb_leds.off()
        YellowLED() # turns off the LED even from PWM
        if run_file_delay_ms:
            display.fill(0)
            display.text('Run file:', 0, 0)
            display.text(filename, 0, 10)
            display.show()
            time.sleep_ms(run_file_delay_ms)
        display.fill(0)
        display.show()
        buzzer.off()
        del_vars()
        from .run_file import run_file
        run_file(filename)

    # Runs the bootloader in the RP2040's Bootrom.
    def run_bootloader():
        rgb_leds.off()
        YellowLED() # turns off the LED even from PWM
        if run_file_delay_ms:
            display.fill(0)
            display.text('Bootloader...', 0, 0)
            display.show()
            time.sleep_ms(run_file_delay_ms)
        display.fill(0)
        display.show()
        import machine
        buzzer.off()
        machine.bootloader()

    # Runs the Python REPL using sys.exit().
    # You can also run the REPL by letting the interpreter reach the end of
    # your program or by sending Ctrl+C to the USB virtual serial port.
    def run_repl():
        rgb_leds.off()
        YellowLED() # turns off the LED even from PWM
        if run_file_delay_ms:
            display.fill(0)
            display.text('exit to REPL...', 0, 0)
            display.show()
            time.sleep_ms(run_file_delay_ms)
        display.fill(0)
        display.show()
        import sys
        sys.exit(0)

    def menu():
        rgb_leds.off()

        from pololu_3pi_2040_robot.extras.menu import Menu
        import os
        from math import exp

        start_ms = time.ticks_ms()
        options = sorted(f for f in os.listdir() if f.endswith(".py") and f != "main.py")
        options += ["bootloader", "exit to REPL"]

        menu = Menu(options)
        menu.display = display
        menu.buzzer = buzzer
        menu.previous_button = button_a
        menu.select_button = button_b
        menu.next_button = button_c
        i = None
        mv = None

        while i == None:
            t = time.ticks_ms()
            elapsed_ms = time.ticks_diff(t, start_ms)

            x = ((elapsed_ms + 1500) % 3000 - 1500) / 1500
            b = exp(-12.5*x*x)

            pwm.duty_u16(65535 - int(b * 65535))

            if not mv or time.ticks_diff(t, mv_time) > 200:
                mv = battery.get_level_millivolts()
                mv_time = t
            if elapsed_ms % 4000 < 2000:
                menu.top_message = 'Run: (^A *B Cv)'
            else:
                menu.top_message = f"Battery: {mv/1000:.2f} V"

            i = menu.update()

        option = options[i]
        if option == "bootloader":
            run_bootloader()
        elif option == "exit to REPL":
            run_repl()
        else:
            run_file(option)

    if button_a.is_pressed():
        run_file("self_test.py")

    button = read_button()

    if button == None and splash_delay_s != 0:
        buzzer.play_in_background(welcome_song)
        button = initial_screen()

    if button == None:
        if default_program:
            run_file(default_program)
        else:
            menu()
    elif button == 'C':
        menu()
    elif button == 'B':
        run_bootloader()
    else: # A
        run_repl()
