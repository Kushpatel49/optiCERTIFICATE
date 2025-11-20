"""
CSS styling for Net Worth Certificate Generator
"""

LIGHT_THEME_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Quicksand', sans-serif !important;
        transition: all 0.2s ease-in-out;
    }

    .stTitle {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }

    .stHeader {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px !important;
    }

    .stSubheader {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px !important;
    }

    .stText {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stMarkdown {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stButton button {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
    }

    .stTextInput input {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stNumberInput input {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stTextArea textarea {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stSelectbox select {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stDateInput input {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stMetric {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stExpander {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stTabs {
        font-family: 'Quicksand', sans-serif !important;
    }

    .stTab {
        font-family: 'Quicksand', sans-serif !important;
    }

    /* Enhanced App Background */
    .stApp {
        background: linear-gradient(135deg, #ffe4b5 0%, #ffd89b 25%, #b0e0e6 50%, #98fb98 75%, #90ee90 100%) !important;
        background-size: 500% 500% !important;
        animation: gradientShift 15s ease infinite !important;
        min-height: 100vh !important;
        padding-top: 0.2rem !important;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Main Container with Card Effect */
    .main .block-container {
        background-color: #ffffff !important;
        color: #212529 !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08) !important;
        padding: 1.5rem 2.5rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        
    }
    
    /* Reduce top padding of Streamlit app */
    .stApp > header {
        padding-top: 0 !important;
    }
    
    /* Reduce space before first element */
    .main .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Enhanced Typography */
    .stTitle, .stHeader, .stSubheader {
        color: #1a1a2e !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }

    .stText {
        color: #495057 !important;
        line-height: 1.7 !important;
    }

    .stMarkdown {
        color: #495057 !important;
        line-height: 1.7 !important;
    }

    .stMarkdown p {
        color: #495057 !important;
        margin-bottom: 0.8rem !important;
    }

    .stMarkdown strong, .stMarkdown b {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }

    b, strong {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }

    /* Enhanced Buttons */
    .stButton button {
        background: linear-gradient(135deg, #ffb347 0%, #ffa07a 100%) !important;
        color: #2c3e50 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 4px 15px rgba(255, 179, 71, 0.3) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 179, 71, 0.4) !important;
        background: linear-gradient(135deg, #ffa07a 0%, #ffb347 100%) !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
    }

    /* Enhanced Form Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select, .stDateInput input {
        background-color: #f8f9fa !important;
        color: #495057 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:hover, .stNumberInput input:hover, .stTextArea textarea:hover, .stSelectbox select:hover {
        border-color: #ffb347 !important;
        background-color: #ffffff !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus, .stDateInput input:focus {
        border-color: #ffb347 !important;
        box-shadow: 0 0 0 4px rgba(255, 179, 71, 0.15) !important;
        background-color: #ffffff !important;
        outline: none !important;
    }

    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa !important;
        border-radius: 16px !important;
        border: none !important;
        padding: 8px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06) !important;
        margin-bottom: 2rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #6c757d !important;
        background-color: transparent !important;
        border: none !important;
        padding: 12px 20px !important;
        margin: 4px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 179, 71, 0.15) !important;
        color: #ff8c00 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffb347 0%, #98fb98 100%) !important;
        color: #2c3e50 !important;
        box-shadow: 0 4px 12px rgba(255, 179, 71, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Enhanced Metrics */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 2px solid #e9ecef !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease !important;
    }

    .stMetric:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12) !important;
        border-color: #98fb98 !important;
    }

    .stMetric .metric-value {
        color: #32cd32 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }

    /* Enhanced Expanders */
    .stExpander {
        background-color: #ffffff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        margin-bottom: 1rem !important;
        overflow: hidden !important;
    }

    .stExpander:hover {
        border-color: #ffb347 !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12) !important;
    }

    .stExpander header {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
        border-radius: 16px 16px 0 0 !important;
        padding: 1rem !important;
        font-weight: 600 !important;
    }

    /* Enhanced Alerts */
    .stAlert {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        color: #0c5460 !important;
        border: 2px solid #bee5eb !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }

    /* Form Labels */
    .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label, .stDateInput label {
        color: #495057 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 0.3px !important;
    }

    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        color: #155724 !important;
        border: 2px solid #c3e6cb !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }

    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        color: #721c24 !important;
        border: 2px solid #f5c6cb !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }

    /* Progress Bars */
    .stProgress > div > div {
        background: linear-gradient(135deg, #ffb347 0%, #98fb98 100%) !important;
        border-radius: 10px !important;
    }

    /* Additional Text Elements */
    .css-1v0mbdj, .css-1v0mbdj * {
        color: #495057 !important;
    }

    .css-1d391kg, .css-1d391kg * {
        color: #495057 !important;
    }

    [data-testid="stMarkdownContainer"] p {
        color: #495057 !important;
    }

    [data-testid="stMarkdownContainer"] strong {
        color: #1a1a2e !important;
    }

    /* Tab Content */
    .stTabs [data-baseweb="tab-panel"] {
        color: #495057 !important;
        padding: 1.5rem 0 !important;
    }

    /* Form Help Text */
    .stTextInput div small, .stNumberInput div small, .stTextArea div small {
        color: #6c757d !important;
        font-size: 13px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 245, 225, 0.9) 100%) !important;
        border-right: 1px solid rgba(255, 179, 71, 0.2) !important;
        box-shadow: 4px 0 15px rgba(0, 0, 0, 0.05) !important;
    }

    /* Full Width Content */
    .main .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Logo Container Enhancement */
    [data-testid="stImage"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0 !important;
    }

    /* Horizontal Rule Enhancement */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #ffb347, #98fb98, transparent) !important;
        margin: 2rem 0 !important;
    }

    /* Column Spacing */
    [data-testid="column"] {
        padding: 0.5rem !important;
    }

    /* Checkbox and Radio */
    .stCheckbox, .stRadio {
        color: #495057 !important;
    }

    .stCheckbox label, .stRadio label {
        font-weight: 500 !important;
    }

    /* Divider Enhancement */
    [data-testid="stHorizontalBlock"] {
        margin: 1rem 0 !important;
    }

    /* Button Text Alignment - Prevent Wrapping */
    .stButton button {
        white-space: nowrap !important;
        text-align: center !important;
        word-wrap: normal !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* Ensure button container doesn't cause wrapping */
    [data-testid="stButton"] {
        width: 100% !important;
    }

    [data-testid="stButton"] > button {
        width: 100% !important;
        min-width: fit-content !important;
    }
    """
