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
        final_analysis = None
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

        # Read solution code
        code_content = ""
        # Default to Hacker_007 for the local session
        solution_path = os.path.join("submissions", "Hacker_007_solution.py")
        if os.path.exists(solution_path):
            try:
                with open(solution_path, "r") as f:
                    code_content = f.read()
            except Exception as e:
                print(f"Warning: Could not read solution file: {e}")

        # Analyze code
        code_score = 0
        if code_content:
            print("\n[Code Analysis] Analyzing submitted code...")
            code_score = analyzer.analyze_code(code_content)
            print(f"Code Quality Score: {code_score}")

        # calculate hard score
        time_score = monitor.calculate_hard_score()
        print(f"\nTime-based Score: {time_score}")
        
        # Weighted average: 50% time, 50% code quality
        if code_score > 0:
            hard_score = int((time_score + code_score) / 2)
        else:
            hard_score = time_score
            
        print(f"Final Hard Score: {hard_score}")
        
        # calculate soft score from final analysis
        if full_text and final_analysis:
            soft_score = round((
                final_analysis.get('coherence', 0) + 
                final_analysis.get('terminology', 0) + 
                final_analysis.get('completeness', 0)
            ) / 3)
            print(f"Soft Score Calculated: {soft_score}")
            print(f"  - Coherence: {final_analysis.get('coherence', 0)}")
            print(f"  - Terminology: {final_analysis.get('terminology', 0)}")
            print(f"  - Completeness: {final_analysis.get('completeness', 0)}")
        else:
            soft_score = 0
            print(f"Soft Score Calculated: {soft_score} (No transcript)")

        verdict = "PASS" if hard_score >= 60 else "FAIL"
        
        real_logger.finish_session(
            hard_score=hard_score, 
            soft_score=soft_score,
            verdict=verdict
        )
        print(f"Full session saved to {real_logger.filepath}")

        # --- Leaderboard Integration ---
        try:
            from src.core.leaderboard import Leaderboard
            
            print("\n" + "*"*50)
            name = input("Session Finalized! Enter your name for the leaderboard: ").strip()
            if name:
                # Get AI overview
                ai_overview = "No analysis available"
                if final_analysis and "comment" in final_analysis:
                    ai_overview = final_analysis["comment"]
                
                lb = Leaderboard()
                lb.add_entry(
                    name=name,
                    hard_score=hard_score,
                    soft_score=soft_score,
                    ai_overview=ai_overview,
                    code_content=code_content
                )
                
                # Update session log with the real name so the certificate uses it
                real_logger.update_candidate_id(name)
                print(f"[Session] Candidate ID updated to: {name}")
                
                lb.display()
            else:
                print("Skipping leaderboard entry.")
        except Exception as e:
            print(f"Leaderboard error: {e}")

if __name__ == "__main__":
    main()
