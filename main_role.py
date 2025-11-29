import threading
import time
from SessionLogger import SessionLogger
from sensor import ActiveWindowMonitor    # Still in development

def main():
    print("Starting GlassBox Session...")
    # logger initialization
    real_logger = SessionLogger(candidate_id="hacker_007")
    
    # sensor initialization
    monitor = ActiveWindowMonitor(real_logger)

    # thread initialization
    t = threading.Thread(target=monitor.run, daemon=True)
    t.start()

    print("Session is LIVE. Press Ctrl+C to finish.")
    
    try:
        # testing for 15 sec
        time.sleep(15) 
    except KeyboardInterrupt:
        print("\nInterrupted by user")

    # stop monitor
    monitor.stop()
    t.join()

    # calculate hard score
    hard_score = monitor.calculate_hard_score()
    print(f"Hard Score Calculated: {hard_score}")

    verdict = "PASS" if hard_score >= 60 else "FAIL"
    
    real_logger.finish_session(
        hard_score=hard_score, 
        soft_score=0, # For now blank
        verdict=verdict
    )
    print(f"Full session saved to {real_logger.filepath}")

if __name__ == "__main__":
    main()