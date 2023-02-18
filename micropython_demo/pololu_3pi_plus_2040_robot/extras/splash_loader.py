def splash_loader(*, default_program, splash_delay_s, run_file_delay_ms):
    welcome_song = "O5e32a16"
    button_a_beep = "!c32"
    button_b_beep = "!e32"
    button_c_beep = "!g32"

    import pololu_3pi_plus_2040_robot as robot
    import time
    import framebuf

    display = robot.Display()
    button_a = robot.ButtonA()
    button_b = robot.ButtonB()
    button_c = robot.ButtonC()
    buzzer = robot.Buzzer()
    buzzer.off()
    robot.RGBLEDs().off()
    robot.YellowLED().off()
   
    def del_vars():
        nonlocal display, button_a, button_b, button_c, buzzer
        del display
        del button_a
        del button_b
        del button_c
        del buzzer

    def initial_screen():
        start = time.ticks_us()
        splash = display.load_pbm("pololu_3pi_plus_2040_robot/extras/splash.pbm")
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
            
            elapsed = time.ticks_us() - start
            countdown_s = splash_delay_s - elapsed//1000000
            if countdown_s <= 0:
                break
            
            display.fill(0)
            if elapsed < 1000000:
                offset = 0
            else:
                offset = max(-32, -32 * (elapsed - 1000000) // 400000)
            display.blit(splash, 0, offset)
            display.text('Push A for files', 0, 68+offset)
            display.text('Default ({}s):'.format(countdown_s), 0, 78+offset)
            display.text('   '+default_program, 0, 88+offset) 

            display.show()
        return None

    def run_file(filename):
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

    def menu():
        from pololu_3pi_plus_2040_robot.extras.menu import Menu
        import os
        options = list(filter(lambda f: f.endswith(".py") and f != "main.py", os.listdir()))
        options += ["bootloader", "exit to REPL"]
        
        menu = Menu(options)
        menu.display = display
        menu.buzzer = buzzer
        menu.previous_button = button_a
        menu.select_button = button_b
        menu.next_button = button_c
        i = None
        while i == None:
            i = menu.update()
        option = options[i]
        if option == "bootloader":
            run_bootloader()
        elif option == "exit to REPL":
            run_repl()
        else:
            run_file(option)

    def run_bootloader():
        display.fill(0)
        display.text('Bootloader...', 0, 0)
        display.show()
        time.sleep_ms(run_file_delay_ms)
        display.fill(0)
        display.show()
        import machine
        machine.bootloader()

    def run_repl():
        display.fill(0)
        display.text('exit to REPL...', 0, 0)
        display.show()
        time.sleep_ms(run_file_delay_ms)
        display.fill(0)
        display.show()

    if splash_delay_s != 0:
        buzzer.play_in_background(welcome_song)
    button = initial_screen()

    if button == None:
        run_file(default_program)
    elif button == "A":
        menu()
    elif button == "B":
        run_bootloader()
    else:
        run_repl()
