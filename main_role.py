import threading
import time
import random
from SessionLogger import SessionLogger
from sensor import ActiveWindowMonitor
from cognitive_engine.clarity_analyzer import ClarityAnalyzer

def main():
    print("Starting GlassBox Session...")
    # logger initialization
    real_logger = SessionLogger(candidate_id="hacker_007")
    
    # sensor initialization
    monitor = ActiveWindowMonitor(real_logger)
    
    # cognitive engine initialization
    analyzer = ClarityAnalyzer(mode="fake")

    # thread initialization
    t = threading.Thread(target=monitor.run, daemon=True)
    t.start()

    print("Session is LIVE. Press Ctrl+C to finish.")
    
    # Mock transcripts for simulation
    mock_transcripts = [
        "I am starting by analyzing the requirements. I need to build a session logger.",
        "Now I'm implementing the class structure. Using dataclasses for events.",
        "I found a bug in the timestamp calculation. Fixing it now.",
        "The code is working. I'm running the tests to verify."
    ]
    
    soft_scores = []

    try:
        # testing for 15 sec
        start_time = time.time()
        transcript_index = 0
        
        while time.time() - start_time < 15:
            # Simulate candidate speaking every ~4 seconds
            if transcript_index < len(mock_transcripts):
                transcript = mock_transcripts[transcript_index]
                print(f"\n[Candidate]: {transcript}")
                
                # Analyze
                analysis = analyzer.analyze(transcript)
                print(f"[Cognitive Engine]: Coherence={analysis['coherence']}, Terminology={analysis['terminology']}")
                
                # Log clarity
                real_logger.log_clarity(analysis)
                
                # Store for final score
                avg_score = (analysis['coherence'] + analysis['terminology'] + analysis['completeness']) / 3
                soft_scores.append(avg_score)
                
                transcript_index += 1
            
            time.sleep(4)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")

    # stop monitor
    monitor.stop()
    t.join()

    # calculate hard score
    hard_score = monitor.calculate_hard_score()
    print(f"\nHard Score Calculated: {hard_score}")
    
    # calculate soft score
    final_soft_score = int(sum(soft_scores) / len(soft_scores)) if soft_scores else 0
    print(f"Soft Score Calculated: {final_soft_score}")

    verdict = "PASS" if hard_score >= 60 and final_soft_score >= 60 else "FAIL"
    
    real_logger.finish_session(
        hard_score=hard_score, 
        soft_score=final_soft_score,
        verdict=verdict
    )
    print(f"Full session saved to {real_logger.filepath}")

if __name__ == "__main__":
    main()