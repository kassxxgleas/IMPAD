import time
import threading

# for now only windows
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
        # type of activities
        self.keywords = {
            "CODING": ["code", "pycharm", "visual studio", "sublime", "vim", ".py", "main.py", "vscode"],
            "RESEARCHING": ["chrome", "firefox", "edge", "stack overflow", "google", "documentation", "gpt", "claude"]
        }

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

    def run(self, interval=1.0):
        self.running = True
        last_state = None
        last_title = ""
        
        print("Sensor linked to Real SessionLogger...")

        while self.running:
            title = self._get_active_window_title()
            new_state = self._classify_state(title)

            if title != last_title:
                
                # Write to log
                self.logger.log_state(new_state)
                
                print(f"// Action: {new_state} | Title changed: {title[:50]}...")
                
                last_state = new_state
                last_title = title

            self.stats[new_state] += interval
            
            time.sleep(interval)

    def stop(self):
        self.running = False

    def calculate_hard_score(self):
        """calculate hard score"""
        total_time = sum(self.stats.values())
        if total_time == 0: 
            return 0
        
        coding = self.stats["CODING"]
        research = self.stats["RESEARCHING"]
        
        # Simple formula (will be changed)
        if coding > research: 
            return 80
        elif research > coding * 2: 
            return 50
        else: 
            return 65
