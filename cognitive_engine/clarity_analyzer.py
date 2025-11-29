"""
ClarityAnalyzer - Main module for analyzing candidate explanations.
Supports both FakeLLM and OpenAI API modes.
"""

import json
import requests
from typing import Dict, Any

from .llm_config import (
    LLM_MODE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    MAX_RETRIES,
    TIMEOUT_SECONDS,
    DEBUG
)
from .fake_llm import FakeLLM
from .system_prompt import get_system_prompt


class ClarityAnalyzer:
    """
    Analyzes candidate explanations using LLM.
    
    Supports two modes:
    - "fake": Uses FakeLLM (no API key needed)
    - "real": Uses OpenAI API (requires API key)
    """
    
    def __init__(self, mode: str = None):
        """
        Initialize ClarityAnalyzer.
        
        Args:
            mode: "fake" or "real" (defaults to LLM_MODE from config)
        """
        self.mode = mode or LLM_MODE
        
        if self.mode not in ["fake", "real"]:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'fake' or 'real'.")
        
        if self.mode == "fake":
            self.llm = FakeLLM()
        elif self.mode == "real":
            if not OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY not set. "
                    "Set it in .env or use mode='fake'"
                )
            self.api_key = OPENAI_API_KEY
            self.model = OPENAI_MODEL
            self.temperature = OPENAI_TEMPERATURE
        
        if DEBUG:
            print(f"[DEBUG] ClarityAnalyzer initialized in {self.mode} mode")
    
    def analyze(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a candidate's explanation.
        
        Args:
            transcript: Candidate's spoken/written explanation
        
        Returns:
            dict: {
                "coherence": int (0-100),
                "terminology": int (0-100),
                "completeness": int (0-100),
                "comment": str
            }
        """
        # Validate input
        if not transcript or len(transcript.strip()) < 5:
            return self._error_response("Transcript too short")
        
        # Choose analysis method
        if self.mode == "fake":
            return self.llm.analyze(transcript)
        else:
            return self._analyze_with_openai(transcript)
    
    def _analyze_with_openai(self, transcript: str, retry_count: int = 0) -> Dict[str, Any]:
        """
        Analyze using OpenAI API.
        
        Args:
            transcript: Text to analyze
            retry_count: Current retry attempt
        
        Returns:
            dict: Analysis result or error response
        """
        try:
            if DEBUG:
                print(f"[DEBUG] Calling OpenAI API (attempt {retry_count + 1})")
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [
                        {"role": "system", "content": get_system_prompt()},
                        {"role": "user", "content": f"Analyze this explanation:\n\n{transcript}"}
                    ]
                },
                timeout=TIMEOUT_SECONDS
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                return self._error_response("Invalid API response structure")
            
            content = data["choices"][0]["message"]["content"]
            
            # if DEBUG:
            #     print(f"[DEBUG] Raw API response: {content}")
            
            # Parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                # Try to extract JSON from response
                result = self._extract_json(content)
                if result is None:
                    return self._error_response(f"Invalid JSON in response: {str(e)}")
            
            # Validate and normalize
            return self._validate_response(result)
        
        except requests.exceptions.Timeout:
            if retry_count < MAX_RETRIES:
                if DEBUG:
                    print(f"[DEBUG] Timeout, retrying... ({retry_count + 1}/{MAX_RETRIES})")
                import time
                time.sleep(2 ** retry_count)
                return self._analyze_with_openai(transcript, retry_count + 1)
            else:
                return self._error_response("API timeout after retries")
        
        except requests.exceptions.ConnectionError as e:
            return self._error_response(f"Connection error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                return self._error_response("Invalid API key")
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                return self._error_response("API rate limit exceeded")
            else:
                return self._error_response(f"HTTP error: {error_msg}")
        
        except Exception as e:
            if DEBUG:
                print(f"[DEBUG] Unexpected error: {type(e).__name__}: {str(e)}")
            return self._error_response(f"Unexpected error: {str(e)}")
    
    def _extract_json(self, text: str) -> Dict[str, Any] | None:
        """
        Try to extract JSON from text (handles markdown blocks, etc.)
        
        Args:
            text: Text that may contain JSON
        
        Returns:
            dict or None
        """
        # Remove markdown code blocks
        text = text.replace("```json", "").replace("```", "")
        
        # Try to find JSON object
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        
        if start_idx == -1 or end_idx == -1:
            return None
        
        json_str = text[start_idx:end_idx + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    
    def _validate_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize LLM response.
        
        Args:
            data: Response dict from LLM
        
        Returns:
            dict: Validated response
        """
        required_fields = ["coherence", "terminology", "completeness", "comment"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return self._error_response(f"Missing field: {field}")
        
        try:
            # Normalize scores to 0-100
            data["coherence"] = max(0, min(100, int(data["coherence"])))
            data["terminology"] = max(0, min(100, int(data["terminology"])))
            data["completeness"] = max(0, min(100, int(data["completeness"])))
            
            # Normalize comment
            data["comment"] = str(data["comment"])[:500]
            
            if DEBUG:
                print(f"[DEBUG] Validated response: {data}")
            
            return data
        
        except (ValueError, TypeError) as e:
            return self._error_response(f"Invalid score format: {str(e)}")
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Return a standard error response.
        
        Args:
            error_msg: Error message
        
        Returns:
            dict: Error response
        """
        return {
            "coherence": 0,
            "terminology": 0,
            "completeness": 0,
            "comment": f"Error: {error_msg}"
        }
