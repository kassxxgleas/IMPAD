import time
import threading

# Пытаемся импортировать библиотеку для окон.
# Если не выходит (например, Mac/Linux без настроек), ставим заглушку.
try:
    import pygetwindow as gw
except ImportError:
    gw = None 

class ActiveWindowMonitor:
    def __init__(self, logger):
        self.logger = logger
        self.running = False
        self.stats = {
            "CODING": 0,
            "RESEARCHING": 0,
            "IDLE": 0
        }
        self.switches = 0  # <--- НОВАЯ ПЕРЕМЕННАЯ: Считаем переключения
        
        self.keywords = {
            "CODING": ["code", "pycharm", "visual studio", "sublime", "vim", ".py", "main.py", "vscode"],
            "RESEARCHING": ["chrome", "firefox", "edge", "stack overflow", "google", "documentation", "gpt", "claude", "yandex"]
        }

    # ... методы _get_active_window_title и _classify_state оставляем те же ...
    def _get_active_window_title(self):
        # (Оставь старый код тут)
        if gw is None: return "Mock Window - Google Chrome"
        try:
            window = gw.getActiveWindow()
            return window.title.lower() if window else ""
        except: return ""

    def _classify_state(self, title):
        # (Оставь старый код тут)
        if not title: return "IDLE"
        title = title.lower()
        for key in self.keywords["CODING"]:
            if key in title: return "CODING"
        for key in self.keywords["RESEARCHING"]:
            if key in title: return "RESEARCHING"
        return "IDLE"

    def run(self, interval=1.0):
        self.running = True
        last_state = None
        last_title = ""
        
        print("👀 Sensor linked to Real SessionLogger...")

        while self.running:
            title = self._get_active_window_title()
            new_state = self._classify_state(title)

            if title != last_title:
                self.logger.log_state(new_state)
                print(f"🔄 Action: {new_state} | Title changed: {title[:50]}...")
                
                # Если сменился именно ТИП деятельности (например, Research -> Coding),
                # засчитываем это как "умственное переключение"
                if new_state != last_state and last_state is not None:
                    self.switches += 1
                
                last_state = new_state
                last_title = title

            self.stats[new_state] += interval
            time.sleep(interval)

    def stop(self):
        self.running = False

    def calculate_hard_score(self):
        """
        ПРОДВИНУТАЯ МЕТРИКА 'AGILE'
        """
        total_time = sum(self.stats.values())
        if total_time == 0: return 0
        
        coding = self.stats["CODING"]
        research = self.stats["RESEARCHING"]
        idle = self.stats["IDLE"]
        
        # 1. База: процент полезного времени (Coding + Research)
        useful_ratio = (coding + research) / total_time
        base_score = 100 * useful_ratio
        
        # 2. Штраф за дисбаланс
        # Если research занимает более 70% времени — штраф 20 баллов
        if research > (coding + research) * 0.7:
            base_score -= 20
            print("⚠️ Penalty: Too much research, little coding.")

        # 3. Бонус за ритм (переключения)
        # Если переключений было достаточно (например, каждые 2-3 минуты), даем бонус
        # Допустим, 1 переключение в минуту - это активная работа.
        switch_rate = self.switches / (total_time / 60) if total_time > 60 else 0
        
        if switch_rate > 0.5: # Чаще чем раз в 2 минуты
            base_score += 10
            print("🔥 Bonus: Good workflow rhythm!")
            
        # Ограничиваем 100 баллами
        return min(100, int(base_score))