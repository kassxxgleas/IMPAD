import speech_recognition as sr
import threading
import time
import os
import numpy as np
import sounddevice as sd
from scipy.io import wavfile as wav

class AudioListener:
    def __init__(self, logger, analyzer):
        self.logger = logger
        self.analyzer = analyzer
        self.recognizer = sr.Recognizer()
        self.running = False
        self.thread = None
        self.fs = 44100  # Sample rate
        self.seconds = 10  # Duration of recording chunk (Increased to 10s)
        self.device_index = None
        
        # Data accumulation
        self.audio_buffer = [] # List of numpy arrays
        self.full_transcript = [] # List of strings
        
        # Auto-detect WO Mic
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and "WO Mic" in dev['name']:
                self.device_index = i
                print(f"[AudioListener] Found WO Mic at index {i}: {dev['name']}")
                break
        
        if self.device_index is None:
            print("[AudioListener] WO Mic not found, using default device.")

    def _listen_loop(self):
        print(f"[AudioListener] Started listening loop (Device Index: {self.device_index})...")
        
        while self.running:
            try:
                # Record audio
                print("[AudioListener] Recording chunk...")
                myrecording = sd.rec(int(self.seconds * self.fs), samplerate=self.fs, channels=1, device=self.device_index)
                sd.wait()  # Wait until recording is finished
                
                # Store raw audio
                self.audio_buffer.append(myrecording)
                
                # Check if silent (simple energy threshold)
                volume_norm = np.linalg.norm(myrecording) * 10
                # print(f"[AudioListener] Volume: {volume_norm:.2f}")
                
                if volume_norm < 0.05: # Lowered threshold significantly
                    print("[AudioListener] Too quiet, skipping...")
                    continue

                # Save as temporary WAV for speech_recognition
                temp_filename = "temp_chunk.wav"
                # Convert to 16-bit PCM for wavfile write
                data = (myrecording * 32767).astype(np.int16)
                wav.write(temp_filename, self.fs, data)
                
                # Transcribe
                with sr.AudioFile(temp_filename) as source:
                    audio_data = self.recognizer.record(source)
                    
                    try:
                        transcript = self.recognizer.recognize_google(audio_data)
                        print("-" * 50)
                        print(f"[Candidate (Voice)]: {transcript}")
                        print("-" * 50)
                        
                        if len(transcript.split()) >= 2:
                            # Accumulate transcript
                            self.full_transcript.append(transcript)
                            
                            # Analyze
                            analysis = self.analyzer.analyze(transcript)
                            print(f"[Cognitive Engine]: Coherence={analysis['coherence']}, Terminology={analysis['terminology']}")
                            self.logger.log_clarity(analysis)
                            
                    except sr.UnknownValueError:
                        # print("[AudioListener] Unintelligible (could not understand audio)")
                        pass # Unintelligible
                    except sr.RequestError:
                        print("[AudioListener] API unavailable")
                
                # Cleanup
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
            except Exception as e:
                print(f"[AudioListener] Error: {e}")
                time.sleep(1)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("[AudioListener] Stopped.")

    def save_recording(self, filename: str):
        """Save the full session audio to a WAV file."""
        if not self.audio_buffer:
            print("[AudioListener] No audio recorded.")
            return
            
        print(f"[AudioListener] Saving full recording to {filename}...")
        try:
            full_audio = np.concatenate(self.audio_buffer, axis=0)
            # Convert to 16-bit PCM
            data = (full_audio * 32767).astype(np.int16)
            wav.write(filename, self.fs, data)
            print("[AudioListener] Recording saved successfully.")
        except Exception as e:
            print(f"[AudioListener] Failed to save recording: {e}")

    def get_full_transcript(self) -> str:
        """Return the full accumulated transcript."""
        return " ".join(self.full_transcript)
