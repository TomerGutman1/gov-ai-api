"""
Test utilities for Government AI API
This script helps test the connection to Supabase and OpenAI services.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
import pandas as pd

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and data retrieval"""
    print("🔍 Testing Supabase connection...")
    
    try:
        # Get credentials
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        # Create client
        supabase = create_client(url, key)
        
        # Test query
        response = supabase.table("israeli_government_decisions").select("*").limit(5).execute()
        
        if response.data:
            print(f"✅ Supabase connected! Found {len(response.data)} records")
            print(f"📊 Sample columns: {list(response.data[0].keys()) if response.data else 'No data'}")
            return True
        else:
            print("⚠️ Supabase connected but no data found in table")
            return True
            
    except Exception as e:
        print(f"❌ Supabase error: {str(e)}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI connection...")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("❌ Missing OpenAI API key in .env file")
            return False
        
        # Create client
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'API connected' in Hebrew"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI connected! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI error: {str(e)}")
        return False

def test_pandasai_integration():
    """Test PandasAI integration with sample data"""
    print("\n🔍 Testing PandasAI integration...")
    
    try:
        import pandas as pd
        from pandasai import SmartDataframe
        from pandasai.llm.openai import OpenAI as PandasAIOpenAI
        
        # Create sample data
        df = pd.DataFrame({
            'decision_id': [1, 2, 3],
            'title': ['החלטה ראשונה', 'החלטה שנייה', 'החלטה שלישית'],
            'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
            'status': ['approved', 'pending', 'approved']
        })
        
        # Initialize PandasAI
        llm = PandasAIOpenAI(api_token=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
        sdf = SmartDataframe(df, config={"llm": llm})
        
        # Test query
        result = sdf.chat("How many approved decisions are there?")
        print(f"✅ PandasAI working! Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ PandasAI error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Government AI API - Connection Tests")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and add your credentials")
        sys.exit(1)
    
    # Run tests
    supabase_ok = test_supabase_connection()
    openai_ok = test_openai_connection()
    pandasai_ok = test_pandasai_integration()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"Supabase: {'✅ Passed' if supabase_ok else '❌ Failed'}")
    print(f"OpenAI: {'✅ Passed' if openai_ok else '❌ Failed'}")
    print(f"PandasAI: {'✅ Passed' if pandasai_ok else '❌ Failed'}")
    
    if all([supabase_ok, openai_ok, pandasai_ok]):
        print("\n✅ All tests passed! Ready to deploy.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())