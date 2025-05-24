"""
Example client for Government AI API
Shows how to interact with the API from Python code.
"""

import requests
import json
from typing import Dict, Any

class GovAIClient:
    """Client for interacting with Government AI API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question about government decisions"""
        response = self.session.post(
            f"{self.base_url}/ask",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded data"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()
    
    def reload_data(self) -> Dict[str, Any]:
        """Reload data from Supabase"""
        response = self.session.post(f"{self.base_url}/reload")
        response.raise_for_status()
        return response.json()

def main():
    """Example usage of the client"""
    # Initialize client
    client = GovAIClient()
    
    print("🔍 Testing Government AI API Client\n")
    
    try:
        # Health check
        print("1. Health Check:")
        health = client.health_check()
        print(json.dumps(health, indent=2))
        print()
        
        # Get statistics
        print("2. Data Statistics:")
        stats = client.get_stats()
        print(json.dumps(stats, indent=2))
        print()
        
        # Ask questions
        questions = [
            "כמה החלטות ממשלה יש במערכת?",
            "What are the most common ministries in the decisions?",
            "מה ההחלטות האחרונות שהתקבלו?",
            "Show me decisions related to technology",
            "אילו החלטות נמצאות בסטטוס 'בתהליך'?"
        ]
        
        print("3. Asking Questions:")
        for i, question in enumerate(questions, 1):
            print(f"\nQ{i}: {question}")
            try:
                result = client.ask_question(question)
                if result["success"]:
                    print(f"A{i}: {result['answer']}")
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Error: {str(e)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()