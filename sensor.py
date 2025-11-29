import time
import threading

# for now only windows
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# keyboard tracking
try:
    from pynput import keyboard
except ImportError:
    keyboard = None


class ActiveWindowMonitor:
    def __init__(self, logger):
        self.logger = logger
        self.running = False
        self.stats = {
            "CODING": 0,
            "RESEARCHING": 0,
            "IDLE": 0
        }
        # type of activities
        self.keywords = {
            "CODING": ["code", "pycharm", "visual studio", "sublime", "vim", ".py", "main.py", "vscode"],
            "RESEARCHING": ["chrome", "firefox", "edge", "stack overflow", "google", "documentation", "gpt", "claude"]
        }
        
        # Keyboard tracking
        self.last_keystroke_time = time.time()
        self.keyboard_listener = None
        self.inactive_typing_periods = 0  # Count of 7+ second inactivity periods
        self.total_inactive_time = 0.0     # Total time spent inactive
        
        # Start keyboard listener if available
        if keyboard:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()

    def _on_key_press(self, key):
        """Callback for keyboard events"""
        self.last_keystroke_time = time.time()

    def _get_active_window_title(self):
        if gw is None:
            return "Mock Window - Google Chrome"
        
        try:
            window = gw.getActiveWindow()
            if window:
                return window.title.lower()
            return ""
        except Exception:
            return ""

    def _classify_state(self, title):
        """classify state by window title"""
        if not title:
            return "IDLE"
        
        title = title.lower()
        
        for key in self.keywords["CODING"]:
            if key in title:
                return "CODING"
        
        for key in self.keywords["RESEARCHING"]:
            if key in title:
                return "RESEARCHING"
            
        return "IDLE"
    
    def _check_keyboard_inactivity(self):
        """Check if user has been inactive on keyboard for more than 7 seconds"""
        time_since_last_key = time.time() - self.last_keystroke_time
        return time_since_last_key > 7.0

    def run(self, interval=1.0):
        self.running = True
        last_state = None
        last_title = ""
        last_inactivity_state = False
        
        print("Sensor linked to Real SessionLogger...")
        if keyboard:
            print("[+] Keyboard tracking enabled (7s inactivity detection)")
        else:
            print("[!] Keyboard tracking disabled (install pynput)")

        while self.running:
            title = self._get_active_window_title()
            new_state = self._classify_state(title)
            
            # Check keyboard inactivity
            is_inactive = self._check_keyboard_inactivity()
            
            # Track inactivity periods
            if is_inactive and not last_inactivity_state:
                # Just became inactive
                self.inactive_typing_periods += 1
                print(f"[PAUSE] Typing inactive for 7+ seconds (count: {self.inactive_typing_periods})")
            
            if is_inactive:
                self.total_inactive_time += interval
            
            last_inactivity_state = is_inactive

            if title != last_title:
                # Write to log
                self.logger.log_state(new_state)
                
                print(f"\\/\\/ Action: {new_state} | Title changed: {title[:50]}...")
                
                last_state = new_state
                last_title = title

            self.stats[new_state] += interval
            
            time.sleep(interval)

    def stop(self):
        self.running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def calculate_hard_score(self):
        """Enhanced hard score calculation"""
        total_time = sum(self.stats.values())
        if total_time == 0:
            return 0
        
        coding_time = self.stats["CODING"]
        research_time = self.stats["RESEARCHING"]
        idle_time = self.stats["IDLE"]
        
        # Productivity ratio (coding + research) / total
        productive_time = coding_time + research_time
        productivity_ratio = productive_time / total_time
        
        # Coding effectiveness: coding / (coding + research)
        if productive_time > 0:
            coding_ratio = coding_time / productive_time
        else:
            coding_ratio = 0
        
        # Base score from productivity (0-50 points)
        productivity_score = productivity_ratio * 50
        
        # Coding balance score (0-50 points)
        # Optimal: 60-80% coding, 20-40% research
        if 0.6 <= coding_ratio <= 0.8:
            balance_score = 50  # Perfect balance
        elif 0.4 <= coding_ratio < 0.6:
            balance_score = 35  # Too much research
        elif 0.8 < coding_ratio <= 1.0:
            balance_score = 40  # Minimal research (ok but not ideal)
        else:
            balance_score = 20  # Imbalanced
        
        # Penalty for excessive idle time (> 20% of total)
        idle_penalty = 0
        if idle_time / total_time > 0.2:
            idle_penalty = -10
        
        # Bonus/penalty for keyboard inactivity patterns
        inactivity_adjustment = self._calculate_inactivity_score()
        
        final_score = int(productivity_score + balance_score + idle_penalty + inactivity_adjustment)
        return max(0, min(100, final_score))
    
    def _calculate_inactivity_score(self):
        """
        Calculate score adjustment based on keyboard inactivity patterns.
        
        Some inactivity is good (thinking/reading), but too much suggests being stuck.
        """
        if self.total_inactive_time == 0:
            return 0
        
        total_time = sum(self.stats.values())
        if total_time == 0:
            return 0
        
        inactive_ratio = self.total_inactive_time / total_time
        
        # Sweet spot: 20-40% thinking time is good
        if 0.2 <= inactive_ratio <= 0.4:
            return 5  # Bonus for thoughtful approach
        elif inactive_ratio < 0.1:
            return -3  # Penalty for rushing (no thinking)
        elif inactive_ratio > 0.6:
            return -10  # Severe penalty for being stuck
        else:
            return 0
    
    def get_keyboard_stats(self):
        """Return keyboard activity statistics"""
        return {
            "inactive_periods": self.inactive_typing_periods,
            "total_inactive_time": round(self.total_inactive_time, 2),
            "inactive_percentage": round(
                (self.total_inactive_time / sum(self.stats.values()) * 100) 
                if sum(self.stats.values()) > 0 else 0, 
                1
            )
        }