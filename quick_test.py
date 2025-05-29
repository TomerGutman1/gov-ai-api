"""Quick test script to verify connections"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Quick Connection Test ===\n")

# Check environment variables
print("1. Checking environment variables:")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

print(f"   Supabase URL: {'✓ Found' if supabase_url else '✗ Missing'}")
print(f"   Supabase Key: {'✓ Found' if supabase_key else '✗ Missing'}")
print(f"   OpenAI Key: {'✓ Found' if openai_key else '✗ Missing'}")

# Test Supabase connection
print("\n2. Testing Supabase connection:")
if supabase_url and supabase_key:
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        # Check the israeli_government_decisions table
        table_name = "israeli_government_decisions"
        try:
            # Get sample data
            response = supabase.table(table_name).select("*").limit(5).execute()
            print(f"   ✓ Connected to table: {table_name}")
            
            if response.data:
                print(f"   ✓ Found {len(response.data)} sample records")
                print(f"   ✓ Table columns: {', '.join(response.data[0].keys())}")
                
                # Get total count
                count_response = supabase.table(table_name).select("*", count='exact').limit(0).execute()
                print(f"   ✓ Total records in table: {count_response.count}")
            else:
                print(f"   ⚠ Table exists but appears to be empty")
                
        except Exception as e:
            print(f"   ✗ Error accessing table: {str(e)}")
    except Exception as e:
        print(f"   ✗ Connection error: {str(e)}")
else:
    print("   ✗ Missing credentials")

# Test OpenAI connection
print("\n3. Testing OpenAI connection:")
if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=5
        )
        print(f"   ✓ OpenAI connected: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ✗ Connection error: {str(e)}")
else:
    print("   ✗ Missing API key")

# Test PandasAI setup
print("\n4. Testing PandasAI integration:")
try:
    import pandas as pd
    from pandasai import SmartDataframe
    from pandasai.llm.openai import OpenAI as PandasAIOpenAI
    
    # Create a small test dataframe
    test_df = pd.DataFrame({
        'decision_number': ['2998', '2993', '2994'],
        'decision_date': ['2025-05-07', '2025-05-05', '2025-05-05']
    })
    
    llm = PandasAIOpenAI(api_token=openai_key, model="gpt-4o")
    sdf = SmartDataframe(test_df, config={"llm": llm})
    
    result = sdf.chat("How many decisions are there?")
    print(f"   ✓ PandasAI working! Test result: {result}")
except Exception as e:
    print(f"   ✗ PandasAI error: {str(e)}")

print("\n✅ Test complete!")
print("\nNext steps:")
print("1. If all tests pass, you can run the API locally with:")
print("   cd app")
print("   python main.py")
print("\n2. Or use Docker:")
print("   docker compose up --build")
