import streamlit as st
from openai import OpenAI
import os
import docx
import PyPDF2
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Document Summarizer POC",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 15px 15px;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .upload-section {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #667eea;
        margin: 2rem 0;
    }
    
    .results-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .summary-content {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        white-space: pre-wrap;
        line-height: 1.6;
        font-family: 'Georgia', serif;
    }
    
    .meta-info {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #666;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable or add it in Streamlit secrets.")
        st.info("💡 In Streamlit Cloud: Go to App Settings → Secrets and add your API key as:\n```\nOPENAI_API_KEY = \"your-api-key-here\"\n```")
        st.stop()
    return OpenAI(api_key=api_key)

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file based on file type"""
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = []
            for page in pdf_reader.pages:
                text.append(page.extract_text())
            return '\n'.join(text)
        
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text from file: {str(e)}")
        return None

def generate_summary(text, summary_type, client):
    """Generate summary using OpenAI API"""
    try:
        if summary_type == "Paragraph":
            prompt = f"""Please summarize the following document in a clear, coherent paragraph format. 
            Focus on the main points, key insights, and conclusions. Make it concise but comprehensive:

            {text}"""
            
        else:  # Bullet Points
            prompt = f"""Please summarize the following document in bullet-point format. 
            Extract the key points and present them as a clear, organized list with proper bullet points:

            {text}"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional document summarizer. Create clear, accurate summaries that capture the essential information from academic papers, business reports, and other professional documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📄 Document Summarizer</h1>
        <p>Upload your documents and get instant summaries in paragraph or bullet-point format</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize OpenAI client
    client = get_openai_client()

    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📁 Upload Your Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'docx'],
            help="Supports .txt, .pdf, and .docx files (max 200MB)"
        )
    
    with col2:
        st.subheader("📝 Summary Format")
        summary_type = st.radio(
            "Choose format:",
            ["Paragraph", "Bullet Points"],
            help="Select how you want your summary formatted"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Process file if uploaded
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size:,} bytes",
            "File type": uploaded_file.type
        }
        
        st.markdown('<div class="meta-info">', unsafe_allow_html=True)
        st.write("**File Information:**")
        for key, value in file_details.items():
            st.write(f"• **{key}:** {value}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Generate summary button
        if st.button("🚀 Generate Summary", key="generate_btn"):
            with st.spinner("📖 Extracting text from your document..."):
                # Extract text
                text = extract_text_from_file(uploaded_file)
                
                if text is None:
                    st.stop()
                
                if len(text.strip()) == 0:
                    st.error("❌ No text found in the uploaded file. Please check your document.")
                    st.stop()
                
                # Check if text is too long
                truncated = False
                if len(text) > 12000:
                    text = text[:12000] + "..."
                    truncated = True
                    st.warning("⚠️ Document was truncated due to length limits.")
            
            with st.spinner("🤖 Generating your summary with AI..."):
                # Generate summary
                summary = generate_summary(text, summary_type, client)
                
                if summary is None:
                    st.stop()
            
            # Display results
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.write("✅ **Summary generated successfully!**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="results-section">', unsafe_allow_html=True)
            
            # Results header
            st.subheader(f"📋 Summary Results ({summary_type} Format)")
            
            # Metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Original Length", f"{len(text):,} chars")
            with col2:
                st.metric("Summary Length", f"{len(summary):,} chars")
            with col3:
                compression_ratio = round((len(summary) / len(text)) * 100, 1)
                st.metric("Compression", f"{compression_ratio}%")
            with col4:
                st.metric("Generated", datetime.now().strftime("%H:%M:%S"))
            
            # Summary content
            st.markdown("**Summary:**")
            st.markdown(f'<div class="summary-content">{summary}</div>', unsafe_allow_html=True)
            
            # Copy button
            st.code(summary, language=None)
            
            if truncated:
                st.info("ℹ️ **Note:** Your document was longer than our current limit, so only the first part was summarized. For the full document summary, consider breaking it into smaller sections.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Success metrics
            st.balloons()

    else:
        # Instructions when no file is uploaded
        st.info("""
        👆 **How to use:**
        1. Upload a document (.txt, .pdf, or .docx)
        2. Choose your preferred summary format
        3. Click "Generate Summary" 
        4. Get your AI-powered summary in seconds!
        
        **Perfect for:**
        • Academic papers and research documents
        • Business reports and proposals  
        • Long articles and whitepapers
        • Meeting transcripts and notes
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🔒 Your documents are processed securely and are not stored or used for training.</p>
        <p>Powered by OpenAI GPT-3.5 • Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
