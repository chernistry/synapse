import requests
import json
from typing import Dict
from .llm_reply_extractor import extract_json_dict_sync

class LlamaAdapter:
    """
    Adapter to interact with a local LLM instance via Ollama.
    """
    def __init__(self, host: str = "http://localhost:11434", model: str = "phi3.5:3.8b"):
        self.api_url = f"{host}/api/generate"
        self.model = model

    def _construct_prompt(self, metrics_summary: Dict) -> str:
        """
        Constructs a prompt for the LLM to generate a new metric profile.

        Args:
            metrics_summary (Dict): A summary of the current system state.

        Returns:
            str: The formatted prompt.
        """
        # This prompt template can be refined.
        prompt = f"""
        System: You are an expert in software engineering and autonomous systems.
        Your task is to act as the core decision-making module for the SYNAPSE agent.
        Based on the following real-time summary of the environment and performance,
        generate a new JSON object with priority weights for the drone's pathfinding mission.

        The weights must be for 'time', 'energy', and 'safety'.
        The weights must sum to 1.0.
        Prioritize safety in cluttered or high-risk environments.
        Prioritize efficiency (time, energy) in open, low-risk environments.

        Current Scenario Summary:
        {json.dumps(metrics_summary, indent=2)}

        Generate ONLY a JSON object with the weights. Format:
        {{"time": 0.3, "energy": 0.3, "safety": 0.4}}
        """
        return prompt

    def generate_metric_profile(self, metrics_summary: Dict) -> Dict[str, float]:
        """
        Queries the LLM to get a new metric profile based on the current situation.

        Args:
            metrics_summary (Dict): A summary of the current system state.

        Returns:
            A dictionary with new weights, or the default if generation fails.
        """
        prompt = self._construct_prompt(metrics_summary)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        default_profile = {'time': 0.4, 'energy': 0.2, 'safety': 0.4}

        try:
            response = requests.post(self.api_url, json=payload, timeout=20)
            response.raise_for_status()
            
            # Debug the raw response
            response_data = response.json()
            raw_response = response_data.get("response", "")
            print(f"[LlamaAdapter] Raw response: {raw_response[:200]}...")
            
            # Use the robust JSON extractor
            new_profile = extract_json_dict_sync(raw_response)
            
            # Validate the profile
            if not new_profile:
                print(f"[LlamaAdapter] Failed to extract profile from response. Using default.")
                return default_profile
                
            # Ensure all required keys are present and values are numeric
            for key in default_profile.keys():
                if key not in new_profile or not isinstance(new_profile[key], (int, float)):
                    print(f"[LlamaAdapter] Missing or invalid key '{key}' in profile. Using default.")
                    return default_profile
            
            # Normalize weights to sum to 1.0
            total = sum(new_profile.values())
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                print(f"[LlamaAdapter] Weights don't sum to 1.0 (sum={total}). Normalizing.")
                for key in new_profile:
                    new_profile[key] = new_profile[key] / total

            print(f"[LlamaAdapter] Successfully generated new metric profile: {new_profile}")
            return new_profile

        except requests.exceptions.RequestException as e:
            print(f"[LlamaAdapter] API call failed: {e}. Using default metric profile.")
            return default_profile
        except json.JSONDecodeError as e:
            print(f"[LlamaAdapter] Failed to decode JSON from response: {e}. Using default.")
            return default_profile
        except Exception as e:
            print(f"[LlamaAdapter] An unexpected error occurred: {e}. Using default.")
            return default_profile

if __name__ == '__main__':
    # Example usage
    adapter = LlamaAdapter()
    summary = {
        "obstacle_density": 0.15,
        "num_dynamic_obstacles": 1,
        "avg_wind_speed": 0.75,
        "max_wind_speed": 1.5
    }
    profile = adapter.generate_metric_profile(summary)
    print("Final Profile:", profile)