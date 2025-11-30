import threading
import time
import random
import os
import sys

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.core.session_logger import SessionLogger
from src.sensors.active_window_monitor import ActiveWindowMonitor
from src.sensors.audio_listener import AudioListener
from src.cognitive.clarity_analyzer import ClarityAnalyzer

def main():
    print("Starting GlassBox Session...")
    # logger initialization
    real_logger = SessionLogger(candidate_id="hacker_007")
    
    # sensor initialization
    monitor = ActiveWindowMonitor(real_logger)
    
    # cognitive engine initialization
    # Mode is now controlled by .env (LLM_MODE)
    analyzer = ClarityAnalyzer()
    print(f"DEBUG: Analyzer Mode is '{analyzer.mode}'")

    # Audio Listener initialization
    listener = AudioListener(real_logger, analyzer)

    # thread initialization
    t = threading.Thread(target=monitor.run, daemon=True)
    t.start()
    
    # Start listening
    listener.start()

    print("Session is LIVE. Speak into your microphone. Press Ctrl+C to finish.")
    
    soft_scores = []

    try:
        while True:
            # Check for stop signal
            if os.path.exists("STOP_SESSION"):
                print("Stop signal received. Ending session...")
                try:
                    os.remove("STOP_SESSION")
                except:
                    pass
                break
                
            # Main thread just waits, audio is processed in background thread
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        print("Stopping session...")
        monitor.stop()
        listener.stop()
        t.join(timeout=1)
        
        # Save full audio
        listener.save_recording(os.path.join("data", "session_audio.wav"))
        
        # Final Analysis
        full_text = listener.get_full_transcript()
        if full_text:
            print("\n[Final Analysis] Analyzing full session...")
            try:
                final_analysis = analyzer.analyze(full_text)
                # Add full transcript to payload
                final_analysis["transcript"] = full_text
                real_logger.log_event("FINAL_ANALYSIS", final_analysis)
                print(f"Final Verdict: {final_analysis.get('comment', 'No comment')}")
            except Exception as e:
                print(f"Final analysis failed: {e}")
        else:
            print("\n[Final Analysis] No transcript available.")

        # calculate hard score
        hard_score = monitor.calculate_hard_score()
        print(f"\nHard Score Calculated: {hard_score}")
        
        # calculate soft score (placeholder logic for now)
        # In a real scenario, this would aggregate the clarity scores
        soft_score = 0 
        print(f"Soft Score Calculated: {soft_score}")

        verdict = "PASS" if hard_score >= 60 else "FAIL"
        
        real_logger.finish_session(
            hard_score=hard_score, 
            soft_score=soft_score,
            verdict=verdict
        )
        print(f"Full session saved to {real_logger.filepath}")

if __name__ == "__main__":
    main()
