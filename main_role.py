import threading
import time
<<<<<<< HEAD
from SessionLogger import SessionLogger  # Код Роли 1
from sensor import ActiveWindowMonitor    # Твой код (Роль 3)

def main():
    print("🚀 Starting GlassBox MVP Session...")
    
    # 1. Инициализация Логгера (Роль 1)
    # Создает файл session_log.json и ставит started_at
    real_logger = SessionLogger(candidate_id="hacker_007")
    
    # 2. Передача Логгера в Сенсор (Роль 3)
    monitor = ActiveWindowMonitor(real_logger)

    # 3. Запуск в потоке
    t = threading.Thread(target=monitor.run, daemon=True)
    t.start()

    print("⏱  Session is LIVE. Press Ctrl+C to finish.")
    
    try:
        # Эмуляция работы (в реале тут будет ждать, пока юзер не нажмет "Стоп")
        # Для теста давай 15 секунд
        time.sleep(15) 
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")

    # 4. Остановка мониторинга
    monitor.stop()
    t.join()

    # 5. ТВОЙ ВКЛАД: Расчет Hard Score
    hard_score = monitor.calculate_hard_score()
    print(f"🏆 Hard Score Calculated: {hard_score}")

    # 6. Финализация (Роль 1)
    # Soft Score пока ставим 0 (ждем Роль 2), Verdict вычисляем
=======
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

>>>>>>> 413bfa5f3f53dc034b429dbda6814e2ffb4ec889
    verdict = "PASS" if hard_score >= 60 else "FAIL"
    
    real_logger.finish_session(
        hard_score=hard_score, 
<<<<<<< HEAD
        soft_score=0, # Заглушка для Роли 2
        verdict=verdict
    )
    print(f"💾 Full session saved to {real_logger.filepath}")
=======
        soft_score=0, # For now blank
        verdict=verdict
    )
    print(f"Full session saved to {real_logger.filepath}")
>>>>>>> 413bfa5f3f53dc034b429dbda6814e2ffb4ec889

if __name__ == "__main__":
    main()