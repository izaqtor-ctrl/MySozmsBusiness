import streamlit as st
import os

st.title("🔧 API Key Diagnostic Tool")

# Try to get the API key
try:
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success(f"✅ Found API key in secrets")
        st.info(f"Key format: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})")
    else:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            st.success(f"✅ Found API key in environment")
            st.info(f"Key format: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})")
        else:
            st.error("❌ No API key found")
            st.stop()
    
    # Clean the API key
    api_key = api_key.strip().strip('"').strip("'")
    st.info(f"Cleaned key: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})")
    
    # Check key format
    if api_key.startswith('sk-'):
        st.success("✅ Key starts with 'sk-'")
    elif api_key.startswith('sk-proj-'):
        st.success("✅ Key starts with 'sk-proj-'")
    else:
        st.error("❌ Key doesn't start with 'sk-' or 'sk-proj-'")
        st.stop()
            
    # Try to import and initialize OpenAI
    try:
        from openai import OpenAI
        st.success("✅ OpenAI library imported successfully")
        
        # Show OpenAI version
        import openai
        st.info(f"OpenAI library version: {openai.__version__}")
        
        with st.spinner("Initializing OpenAI client..."):
            # Try multiple initialization methods to work around the proxies issue
            client = None
            
            # Method 1: Try basic initialization
            try:
                client = OpenAI(api_key=api_key)
                st.success("✅ OpenAI client initialized successfully (Method 1)")
            except TypeError as e:
                if "proxies" in str(e):
                    st.warning("⚠️ Method 1 failed due to proxies argument")
                    
                    # Method 2: Try with explicit None for problematic args
                    try:
                        import inspect
                        # Get the OpenAI constructor signature
                        sig = inspect.signature(OpenAI.__init__)
                        
                        # Create kwargs with only the api_key
                        kwargs = {"api_key": api_key}
                        
                        client = OpenAI(**kwargs)
                        st.success("✅ OpenAI client initialized successfully (Method 2)")
                    except Exception as e2:
                        st.error(f"Method 2 also failed: {str(e2)}")
                        
                        # Method 3: Last resort - try importing differently
                        try:
                            from openai.lib._old_api import OpenAI as OldOpenAI
                            client = OldOpenAI(api_key=api_key)
                            st.success("✅ OpenAI client initialized successfully (Method 3 - Legacy)")
                        except Exception as e3:
                            st.error(f"All methods failed. Final error: {str(e3)}")
                            st.error("This appears to be a Streamlit Cloud environment issue.")
                else:
                    st.error(f"Unexpected TypeError: {str(e)}")
            except Exception as e:
                st.error(f"Non-TypeError exception: {str(e)}")
            
            if not client:
                st.error("❌ Could not initialize OpenAI client with any method")
                st.info("""
                **This is likely a Streamlit Cloud environment issue. Try:**
                1. Using a different deployment platform (like Railway, Render, or Heroku)
                2. Running locally instead
                3. Waiting for Streamlit Cloud to update their environment
                """)
                st.stop()
        st.success("✅ OpenAI client initialized successfully")
        
        # Try a simple API call
        if st.button("🚀 Test API Call"):
            try:
                with st.spinner("Making API call..."):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Say exactly: 'Test successful'"}],
                        max_tokens=10,
                        temperature=0
                    )
                st.success(f"✅ API call successful!")
                st.write(f"**Response:** {response.choices[0].message.content}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ API call failed: {str(e)}")
                st.info("This suggests an issue with your API key permissions or account status.")
                
    except Exception as e:
        st.error(f"❌ OpenAI client initialization failed: {str(e)}")
        st.info("**Possible causes:**")
        st.write("• API key is invalid or revoked")
        st.write("• No billing/credits set up on your OpenAI account")  
        st.write("• Rate limits exceeded")
        st.write("• Account suspended")
        
except Exception as e:
    st.error(f"❌ General error: {str(e)}")

# Instructions
st.markdown("---")
st.markdown("""
### 🛠️ **Troubleshooting Steps:**

1. **Check your API key at:** https://platform.openai.com/api-keys
2. **Verify billing setup at:** https://platform.openai.com/usage  
3. **Make sure you have credits/free usage remaining**
4. **Try creating a new API key if this one is old**

### 📋 **Expected Key Format:**
- Starts with `sk-` or `sk-proj-`
- Length: usually 48-56 characters
- No extra spaces or quotes

### 🔐 **In Streamlit Secrets, format should be:**
```
OPENAI_API_KEY = "sk-your-actual-key-here"
```
""")

if st.button("🔄 Refresh Test"):
    st.rerun()
