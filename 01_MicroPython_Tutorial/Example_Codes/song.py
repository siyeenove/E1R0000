from machine import Pin, PWM
import time

class MusicPlayer:
    """
    Music player class
    Can play simple melodies
    """
    
    # Note frequency definitions (Hz)
    NOTES = {
        'C4': 261.63,
        'C#4': 277.18,
        'D4': 293.66,
        'D#4': 311.13,
        'E4': 329.63,
        'F4': 349.23,
        'F#4': 369.99,
        'G4': 392.00,
        'G#4': 415.30,
        'A4': 440.00,
        'A#4': 466.16,
        'B4': 493.88,
        'C5': 523.25,
        'C#5': 554.37,
        'D5': 587.33,
        'D#5': 622.25,
        'E5': 659.25,
        'F5': 698.46,
        'F#5': 739.99,
        'G5': 783.99,
        'G#5': 830.61,
        'A5': 880.00,
        'A#5': 932.33,
        'B5': 987.77,
        'C6': 1046.50,
        'REST': 0  # Rest (silence)
    }
    
    # Note duration definitions (milliseconds)
    TEMPO = {
        'whole': 1600,      # Whole note
        'half': 800,        # Half note
        'quarter': 400,     # Quarter note
        'eighth': 200,      # Eighth note
        'sixteenth': 100,   # Sixteenth note
        'thirtysecond': 50  # Thirty-second note
    }
    
    def __init__(self, pin_num, tempo=120):
        """
        Initialize music player
        
        Parameters:
            pin_num: GPIO pin number
            tempo: Beats per minute
        """
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = PWM(self.pin)
        self.set_tempo(tempo)
        
    def set_tempo(self, tempo):
        """
        Set playback speed
        
        Parameters:
            tempo: Beats per minute
        """
        # Update all note durations
        base_duration = 60000 / tempo  # Quarter note duration in milliseconds
        
        self.TEMPO = {
            'whole': int(base_duration * 4),
            'half': int(base_duration * 2),
            'quarter': int(base_duration),
            'eighth': int(base_duration / 2),
            'sixteenth': int(base_duration / 4),
            'thirtysecond': int(base_duration / 8)
        }
        
    def play_note(self, note, duration_type='quarter', volume=50):
        """
        Play a single note
        
        Parameters:
            note: Note name (e.g., 'C4', 'E5', 'REST')
            duration_type: Duration type
            volume: Volume (0-100)
        """
        if note in self.NOTES:
            freq = int(self.NOTES[note])
            if freq == 0:
                # Rest (silence)
                self.pwm.duty(0)
            else:
                # Play note
                self.pwm.freq(freq)
                self.pwm.duty(int(volume * 10.23))
            
            # Hold note duration
            time.sleep_ms(self.TEMPO.get(duration_type, 400))
            
            # Stop sound
            self.pwm.duty(0)
            
            # Small gap between notes (prevents sticking)
            time.sleep_ms(10)
        else:
            print(f"Unknown note: {note}")
    
    def play_melody(self, melody):
        """
        Play a melody
        
        Parameters:
            melody: Melody list, each element is (note, duration_type) or (note, duration_type, volume)
        Example:
            [('C4', 'quarter'), ('E4', 'quarter'), ('G4', 'half')]
        """
        for note_info in melody:
            if len(note_info) == 2:
                note, duration = note_info
                self.play_note(note, duration)
            elif len(note_info) == 3:
                note, duration, volume = note_info
                self.play_note(note, duration, volume)
    
    def play_song(self, song_name='happy_birthday'):
        """Play preset songs"""
        songs = {
            'happy_birthday': [
                ('C4', 'eighth'), ('C4', 'eighth'), ('D4', 'quarter'), ('C4', 'quarter'), ('F4', 'quarter'),
                ('E4', 'half'), ('C4', 'eighth'), ('C4', 'eighth'), ('D4', 'quarter'), ('C4', 'quarter'),
                ('G4', 'quarter'), ('F4', 'half'), ('C4', 'eighth'), ('C4', 'eighth'), ('C5', 'quarter'),
                ('A4', 'quarter'), ('F4', 'quarter'), ('E4', 'quarter'), ('D4', 'quarter'), ('A#4', 'eighth'),
                ('A#4', 'eighth'), ('A4', 'quarter'), ('F4', 'quarter'), ('G4', 'quarter'), ('F4', 'half')
            ],
            
            'twinkle_star': [
                ('C4', 'quarter'), ('C4', 'quarter'), ('G4', 'quarter'), ('G4', 'quarter'),
                ('A4', 'quarter'), ('A4', 'quarter'), ('G4', 'half'), ('F4', 'quarter'),
                ('F4', 'quarter'), ('E4', 'quarter'), ('E4', 'quarter'), ('D4', 'quarter'),
                ('D4', 'quarter'), ('C4', 'half')
            ],
            
            'mario': [
                ('E5', 'eighth'), ('E5', 'eighth'), ('REST', 'eighth'), ('E5', 'eighth'),
                ('REST', 'eighth'), ('C5', 'eighth'), ('E5', 'quarter'), ('G5', 'quarter'),
                ('REST', 'quarter'), ('G4', 'quarter'), ('REST', 'quarter')
            ]
        }
        
        if song_name in songs:
            print(f"Playing: {song_name}")
            self.play_melody(songs[song_name])
        else:
            print(f"Song not found: {song_name}")
    
    def deinit(self):
        """Release resources"""
        self.pwm.duty(0)
        self.pwm.deinit()

# Usage example
def test_music():
    player = MusicPlayer(pin_num=9)
    try:
        # Play Happy Birthday
        player.play_song('happy_birthday')
        time.sleep(1)
        
        # Play Twinkle Twinkle Little Star
        player.play_song('twinkle_star')
        time.sleep(1)
        
        # Play Mario theme
        player.play_song('mario')
        time.sleep(1)
        
        # Custom melody
        print("Playing custom melody...")
        custom_melody = [
            ('C4', 'quarter', 80),
            ('E4', 'quarter', 80),
            ('G4', 'quarter', 80),
            ('C5', 'half', 100),
            ('G4', 'quarter', 80),
            ('E4', 'quarter', 80),
            ('C4', 'half', 60)
        ]
        player.play_melody(custom_melody)
        
    finally:
        player.deinit()
        print("Music playback completed")

# Avoid interfering with the servo
left_key = Pin(4, Pin.OUT)
left_key = Pin(5, Pin.OUT)
left_key = Pin(6, Pin.OUT)
left_key = Pin(7, Pin.OUT)

# Play the music once
test_music()

