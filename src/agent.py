"""
Google Gemini Music Agent - Orchestrates music recommendations through conversation.

This module implements a conversational AI agent powered by Google Gemini (new google.genai) that:
1. Engages in multi-turn dialogue with users
2. Extracts music preferences from natural language
3. Orchestrates API calls to Spotify and your recommender
4. Manages conversation history for context awareness

The agent acts as the "brain" of the system, understanding user intent
and coordinating all other components (Spotify API, recommender scoring).
"""

import os
import json
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
# This loads GEMINI_API_KEY, SPOTIFY_CLIENT_ID, etc.
load_dotenv(verbose=False)


class MusicAgent:
    """
    Conversational AI agent for music recommendations.

    Uses Google Gemini to understand user preferences and orchestrate
    Spotify searches + recommendation scoring.

    Attributes:
        client: Google Gemini client instance
        conversation_history: List of conversation turns (user/assistant messages)
        system_prompt: Instructions that define the agent's personality and behavior
    """

    def __init__(self):
        """
        Initialize the Music Agent with Google Gemini API (new google.genai package).

        Sets up:
        - API client (uses GEMINI_API_KEY from .env)
        - Empty conversation history (fresh conversation each time)
        - System prompt (tells Gemini how to behave)
        """
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Check your .env file!")

        # Create Gemini client with the google.genai package
        self.client = genai.Client(api_key=api_key)

        # Store conversation history for multi-turn context
        # Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        self.conversation_history = []

        # System prompt - SHORTENED to reduce token usage
        # Gemini's free tier has strict token limits, so be concise
        self.system_prompt = """You are VibeFinder, a music recommendation AI.
Extract music preferences (mood, genre, energy, valence, danceability, acousticness) from user input.
Respond conversationally, then return JSON with extracted preferences.

Format: {"preferences": {mood, genre, energy, valence, danceability, acousticness}, "user_message": "response", "ready_to_recommend": true/false}
Values: mood/genre=string, others=0-1 scale. Ask questions if unclear."""

    def chat(self, user_message: str) -> dict:
        """
        Send a message to Gemini and get a response.

        This implements the core conversation loop:
        1. Add user message to history
        2. Send to Gemini with system prompt
        3. Get Gemini's response
        4. Add response to history
        5. Parse and return response

        Args:
            user_message (str): What the user typed (e.g., "I want upbeat lo-fi")

        Returns:
            dict: Gemini's response containing:
                - "user_message": What the user said
                - "agent_response": What Gemini said
                - "preferences": Extracted music preferences (if available)
                - "ready_to_recommend": Whether we have enough info to recommend

        Example:
            agent = MusicAgent()
            response = agent.chat("I want chill lo-fi beats")
            print(response["agent_response"])  # Gemini's conversational reply
            print(response["preferences"])     # Extracted mood, genre, energy, etc.
        """

        # Step 1: Add user message to conversation history
        # This ensures Gemini remembers context from previous messages
        self.conversation_history.append({
            "role": "user",
            "parts": [user_message]  # Gemini uses "parts" not "content"
        })

        # Step 2: Build full message with system prompt
        # Gemini doesn't have a separate system parameter, so we prepend it to the message
        full_prompt = f"{self.system_prompt}\n\nUser: {user_message}"

        # Step 3: Send to Gemini using the new google.genai client
        # The new API is simpler: client.models.generate_content()
        try:
            response = self.client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=full_prompt
            )
            assistant_message = response.text
        except Exception as e:
            # Handle rate limiting or other errors gracefully
            print(f"Error calling Gemini API: {e}")
            assistant_message = "Sorry, I encountered an error. Please try again."

        # Step 4: Add Gemini's response to conversation history
        # This ensures future messages include context of past exchanges
        self.conversation_history.append({
            "role": "model",  # Gemini uses "model" not "assistant"
            "parts": [assistant_message]
        })

        # Step 5: Parse Gemini's response
        # Gemini may return JSON with preferences + conversational text
        # Try to extract structured data if present
        parsed_response = self._parse_response(assistant_message)

        return {
            "user_message": user_message,
            "agent_response": parsed_response.get("user_message", assistant_message),
            "preferences": parsed_response.get("preferences"),
            "ready_to_recommend": parsed_response.get("ready_to_recommend", False)
        }

    def _parse_response(self, response_text: str) -> dict:
        """
        Extract structured data from Gemini's response.

        Gemini returns text that may contain JSON with extracted preferences.
        This function tries to extract that JSON.

        Args:
            response_text (str): Gemini's full response text

        Returns:
            dict: Parsed response with extracted preferences, or empty dict if parsing fails

        Example:
            Gemini might respond with:
            ```json
            {
                "preferences": {"mood": "happy", "genre": "pop", ...},
                "user_message": "You want happy pop! Let me search...",
                "ready_to_recommend": true
            }
            ```
            This function extracts that JSON.
        """
        try:
            # Try to find JSON in Gemini's response
            # Gemini might embed JSON between markdown code blocks: ```json ... ```
            if "```json" in response_text:
                # Extract text between ```json and ```
                start = response_text.find("```json") + 7  # Skip "```json"
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
                parsed = json.loads(json_str)
                return parsed
            elif "{" in response_text:
                # Try to parse raw JSON if no code block markers
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                parsed = json.loads(json_str)
                return parsed
        except (json.JSONDecodeError, ValueError):
            # If parsing fails, just return the text as-is
            # This is fine - Gemini's conversational response is still useful
            pass

        # If no JSON found or parsing failed, return simple dict with the response text
        return {"user_message": response_text}

    def get_conversation_history(self) -> list:
        """
        Get the full conversation history so far.

        Useful for debugging or analyzing what the agent has learned about user preferences.

        Returns:
            list: List of dicts with "role" and "parts" keys

        Example:
            history = agent.get_conversation_history()
            for msg in history:
                print(f"{msg['role']}: {msg['parts']}")
        """
        return self.conversation_history

    def reset_conversation(self) -> None:
        """
        Clear conversation history and start fresh.

        Useful when you want to start a new conversation with different preferences.

        Example:
            agent.reset_conversation()
            # Now talking to a different user
            agent.chat("I like heavy metal")
        """
        self.conversation_history = []
        print("Conversation reset. Starting fresh!")

    def extract_preferences_only(self, user_message: str) -> dict:
        """
        Extract music preferences from a single message without full conversation.

        Sometimes you just want to extract preferences from one message
        without managing conversation history. This method does that.

        Args:
            user_message (str): User's description of music taste

        Returns:
            dict: Extracted preferences (mood, genre, energy, etc.)

        Example:
            prefs = agent.extract_preferences_only("upbeat indie pop with good energy")
            print(prefs["mood"])    # "energetic"
            print(prefs["genre"])   # "indie pop"
        """
        # Create a one-off request to Gemini (doesn't affect conversation history)
        extraction_prompt = f"""
Extract music preferences from this message: "{user_message}"

Return ONLY valid JSON (no other text) with these fields:
{{
    "artist": "string or null if not mentioned",
    "mood": "string - MUST be one of: sad, energetic, chill, neutral",
    "genre": "string",
    "energy": 0.0-1.0,
    "valence": 0.0-1.0,
    "danceability": 0.0-1.0,
    "acousticness": 0.0-1.0
}}

CRITICAL: Normalize the mood to standard moods:
- "sad", "down", "melancholy", "breakup", "depressed" → "sad"
- "happy", "joyful", "upbeat", "energetic", "excited", "fun", "pumped" → "energetic"
- "chill", "relaxed", "mellow", "laid-back", "calm", "lofi" → "chill"
- anything else → "neutral"

Fill in what you can infer. Leave null for unknown values.
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=extraction_prompt
            )
            response_text = response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return {}

        # Try to parse the JSON response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                json_str = response_text

            preferences = json.loads(json_str)
            return preferences
        except json.JSONDecodeError:
            # If parsing fails, return empty dict
            print(f"Warning: Could not parse preferences from: {response_text}")
            return {}


def main():
    """
    Simple example showing how to use the MusicAgent.

    This demonstrates:
    - Creating an agent
    - Having a multi-turn conversation
    - Extracting preferences
    - Resetting conversation
    """

    # Create the agent
    print("🎵 VibeFinder Music Agent")
    print("=" * 50)
    agent = MusicAgent()

    # Example 1: Multi-turn conversation
    print("\n--- Example 1: Multi-turn conversation ---")

    # Turn 1: User describes mood
    response1 = agent.chat("I'm in a chill mood")
    print(f"\nUser: {response1['user_message']}")
    print(f"Agent: {response1['agent_response']}")
    print(f"Preferences so far: {response1['preferences']}")

    # Turn 2: User adds more detail
    response2 = agent.chat("I like lo-fi beats with good energy")
    print(f"\nUser: {response2['user_message']}")
    print(f"Agent: {response2['agent_response']}")
    print(f"Preferences: {response2['preferences']}")

    # Example 2: Extract preferences from a single message
    # print("\n--- Example 2: Quick preference extraction ---")
    # agent.reset_conversation()
    #
    # prefs = agent.extract_preferences_only("upbeat indie pop with acoustic vibes")
    # print(f"Extracted: {prefs}")

    # Example 3: View conversation history
    # print("\n--- Example 3: Conversation history ---")
    # history = agent.get_conversation_history()
    # print(f"Total messages in conversation: {len(history)}")
    # for i, msg in enumerate(history, 1):
    #     print(f"  {i}. {msg['role']}: {msg['content'][:50]}...")


if __name__ == "__main__":
    main()