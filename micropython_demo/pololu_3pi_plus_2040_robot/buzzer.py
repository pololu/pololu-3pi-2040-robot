from machine import Pin, PWM
import machine
import time

pwm = PWM(Pin(7, Pin.OUT))
user_callback = lambda v, f: None
is_playing = False

volumes = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 64, 128]

class Buzzer:
    def __init__(self):
        global pwm
        self.pwm = pwm
        self.off()

    def is_playing(self):
        global is_playing
        return is_playing

    def set_callback(self, f):
        global user_callback
        user_callback = f

    def beep(self):
        self.pwm.freq(440)
        self.pwm.duty_u16(32767)
        time.sleep_ms(100)
        self.pwm.duty_u16(0)

    def on(self):
        self.pwm.freq(200)
        self.pwm.duty_u16(32767)

    def off(self):
        global is_playing
        if is_playing:
            timer.deinit()
            is_playing = False
        self.pwm.duty_u16(0)

    def play(self, notes):
        global is_playing
        try:
            self.play_in_background(notes)
            while is_playing:
                pass
        finally:
            self.off()

    def play_in_background(self, notes):
        global i, f, v, d, note_count, timer, is_playing
        notes = notes.lower()

        if is_playing:
            timer.deinit()

        f = []  # pre-computed list of frequencies
        d = []  # pre-computed list of durations
        v = []  # pre-computed list of volumes

        x = 0

        octave = 4
        octave_boost = 0
        volume = 15
        staccato = False
        tempo = 120
        default_duration = 4

        notelen = len(notes)
        while x < notelen:
            c = notes[x]
            x += 1
            num_string = ""

            accidentals = 0
            if x < notelen and (notes[x] == '+' or notes[x] == '#'):
                accidentals += 1
                x += 1
            elif x < notelen and notes[x] == '-':
                accidentals -= 1
                x += 1

            while x < notelen and notes[x].isdigit():
                num_string += notes[x]
                x += 1
            num = int(num_string) if num_string != "" else 0

            note = octave * 12
            if "c" == c:
                note += 0
            elif "d" == c:
                note += 2
            elif "e" == c:
                note += 4
            elif "f" == c:
                note += 5
            elif "g" == c:
                note += 7
            elif "a" == c:
                note += 9
            elif "b" == c:
                note += 11
            elif "r" == c:
                note = 0
            elif ">" == c:
                octave_boost += 1
                continue
            elif "<" == c:
                octave_boost -= 1
                continue
            elif "t" == c:
                tempo = num
                continue
            elif "v" == c:
                volume = min(num, 15)
                continue
            elif "o" == c:
                octave = num
                continue
            elif "l" == c:
                default_duration = min(num, 2000)
                continue
            elif "m" == c:
                staccato = x < notelen and notes[x] == 's'
                x += 1
                continue
            elif "!" == c:
                octave = 4
                volume = 15
                staccato = False
                tempo = 120
                default_duration = 4
                octave_boost = 0
                continue
            else:
                continue

            note += octave_boost*12
            note += accidentals

            duration_type = 1
            if num > 0 and num <= 2000:
                duration_type = num
            else:
                duration_type = default_duration
            duration = 60000/tempo/(duration_type/4)

            if x < notelen and notes[x] == '.':
                duration += duration/2
                x += 1

            if note == 0:
                f.append(0)
                v.append(0)
            else:
                freq = round(440 * 2**((note - 57)/12))
                f.append(freq)
                v.append(volumes[volume])
            d.append(round(duration/2 if staccato else duration))

            if staccato:
                f.append(0)
                d.append(round(duration/2))
                v.append(0)

            octave_boost = 0
        # end of loop

        is_playing = True
        i = 0
        note_count = len(f)
        timer = machine.Timer()
        timer.init(period=1, mode=machine.Timer.ONE_SHOT, callback=callback)

def callback(t):
    global pwm, i, f, v, d, note_count, is_playing

    if i >= note_count:
        pwm.duty_u16(0)
        is_playing = False
        return

    if f[i]:
        pwm.freq(f[i])
    pwm.duty_u16(v[i]*256)
    user_callback(v[i], f[i])
    t.init(period=d[i], mode=machine.Timer.ONE_SHOT, callback=callback)
    i += 1
