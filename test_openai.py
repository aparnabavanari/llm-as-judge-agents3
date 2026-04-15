"""
Test OpenAI API Integration

Quick test to verify OpenAI API is configured correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.base_agent import BaseLLMAgent


class TestAgent(BaseLLMAgent):
    """Simple test agent"""
    
    def execute(self):
        """Test LLM call"""
        system_prompt = "You are a helpful assistant that responds in JSON format."
        user_prompt = """
        Please respond with a JSON object containing:
        {
            "status": "success",
            "message": "OpenAI API is working correctly!",
            "model": "name of the model you are"
        }
        """
        
        return self.call_llm(system_prompt, user_prompt, temperature=0.3)


def main():
    print("\n" + "="*70)
    print("OpenAI API Integration Test")
    print("="*70 + "\n")
    
    try:
        # Initialize agent
        print("1. Initializing agent...")
        agent = TestAgent(model_name="gpt-4-turbo")
        print("   ✓ Agent initialized successfully\n")
        
        # Test API call
        print("2. Testing OpenAI API call...")
        response = agent.execute()
        print("   ✓ API call successful!\n")
        
        # Display response
        print("3. Response from OpenAI:")
        print("-"*70)
        for key, value in response.items():
            print(f"   {key}: {value}")
        print("-"*70 + "\n")
        
        print("✅ SUCCESS: OpenAI API integration is working correctly!\n")
        print("You can now run: python run.py")
        print("="*70 + "\n")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ ERROR: {e}\n")
        print("Please check that:")
        print("  1. .env file exists in the project root")
        print("  2. OPENAI_API_KEY is set in .env file")
        print("  3. API key is valid (starts with 'sk-')\n")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        print("Common issues:")
        print("  1. Invalid or expired API key")
        print("  2. No billing enabled on OpenAI account")
        print("  3. Network connectivity issues")
        print("  4. Model access restrictions\n")
        print(f"Error type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
