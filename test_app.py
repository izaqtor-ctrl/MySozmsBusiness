import streamlit as st
import os

st.title("🔧 API Key Test")

# Try to get the API key
try:
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success(f"✅ Found API key in secrets (starts with: {api_key[:7]}...)")
    else:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            st.success(f"✅ Found API key in environment (starts with: {api_key[:7]}...)")
        else:
            st.error("❌ No API key found")
            st.stop()
            
    # Try to import and initialize OpenAI
    try:
        from openai import OpenAI
        st.success("✅ OpenAI library imported successfully")
        
        client = OpenAI(api_key=api_key)
        st.success("✅ OpenAI client initialized successfully")
        
        # Try a simple API call
        if st.button("Test API Call"):
            with st.spinner("Testing API..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Say 'API test successful!'"}],
                    max_tokens=10
                )
                st.success(f"✅ API call successful: {response.choices[0].message.content}")
                
    except Exception as e:
        st.error(f"❌ OpenAI initialization failed: {str(e)}")
        
except Exception as e:
    st.error(f"❌ General error: {str(e)}")

st.info("If this test passes, the main app should work too!")
