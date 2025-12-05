#!/usr/bin/env python
# src/app.py
import os
import sys
import streamlit as st
import requests
from datetime import datetime
from pathlib import Path
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crew import ResearchCrew, create_llm

# Page configuration
st.set_page_config(
    page_title="Financial Research AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern glassmorphism design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');
    
    :root {
        --bg-dark: #050508;
        --bg-card: rgba(15, 15, 25, 0.7);
        --bg-card-hover: rgba(25, 25, 40, 0.8);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-shadow: rgba(0, 0, 0, 0.4);
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --accent-tertiary: #a855f7;
        --accent-cyan: #22d3ee;
        --accent-emerald: #34d399;
        --accent-amber: #fbbf24;
        --accent-rose: #fb7185;
        --text-white: #ffffff;
        --text-light: #e2e8f0;
        --text-muted: #94a3b8;
        --text-dim: #64748b;
    }
    
    /* Main app background with animated gradient */
    .stApp {
        background: var(--bg-dark);
        background-image: 
            radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(34, 211, 238, 0.05) 0%, transparent 70%);
        background-attachment: fixed;
    }
    
    /* Hide only menu and footer, keep header controls */
    #MainMenu, footer {visibility: hidden;}
    
    /* Keep header transparent but show all controls */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 10, 20, 0.95) 0%, rgba(5, 5, 15, 0.98) 100%);
        border-right: 1px solid var(--glass-border);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    
    /* Logo and branding */
    .sidebar-logo {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .sidebar-logo-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        display: block;
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.5));
    }
    
    .sidebar-logo-text {
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-primary) 50%, var(--accent-tertiary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    
    .sidebar-logo-subtitle {
        font-family: 'Fira Code', monospace;
        font-size: 0.7rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 0.25rem;
    }
    
    /* Section containers */
    .sidebar-section {
        background: var(--bg-card);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.25rem;
        margin: 0 0.5rem 1rem 0.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .sidebar-section:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .section-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 10px;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    /* Connection status indicator */
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1rem;
        background: rgba(34, 211, 238, 0.1);
        border: 1px solid rgba(34, 211, 238, 0.2);
        border-radius: 10px;
        margin-top: 0.75rem;
    }
    
    .connection-status.error {
        background: rgba(251, 113, 133, 0.1);
        border-color: rgba(251, 113, 133, 0.2);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-emerald);
        box-shadow: 0 0 8px var(--accent-emerald);
        animation: pulse 2s infinite;
    }
    
    .status-dot.error {
        background: var(--accent-rose);
        box-shadow: 0 0 8px var(--accent-rose);
        animation: none;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.95); }
    }
    
    .status-text {
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
        color: var(--accent-cyan);
    }
    
    .status-text.error {
        color: var(--accent-rose);
    }
    
    /* Model card */
    .model-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.75rem;
    }
    
    .model-name {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-white);
        margin-bottom: 0.25rem;
    }
    
    .model-meta {
        font-family: 'Fira Code', monospace;
        font-size: 0.7rem;
        color: var(--accent-cyan);
    }
    
    /* Agent cards */
    .agent-grid {
        display: grid;
        gap: 0.6rem;
    }
    
    .agent-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--glass-border);
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    .agent-item:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateX(4px);
    }
    
    .agent-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-size: 1rem;
    }
    
    .agent-icon.research { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
    .agent-icon.analyst { background: linear-gradient(135deg, #22d3ee, #06b6d4); }
    .agent-icon.data { background: linear-gradient(135deg, #34d399, #10b981); }
    .agent-icon.writer { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
    
    .agent-info {
        flex: 1;
    }
    
    .agent-name {
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        color: var(--text-light);
    }
    
    .agent-role {
        font-family: 'Fira Code', monospace;
        font-size: 0.65rem;
        color: var(--text-dim);
    }
    
    /* Main content area */
    .main-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem 1rem 3rem 1rem;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        background: linear-gradient(135deg, var(--text-white) 0%, var(--accent-cyan) 50%, var(--accent-tertiary) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin: 0 0 1rem 0;
        text-align: center;
        width: 100%;
    }
    
    .main-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(0.9rem, 2vw, 1.15rem);
        font-weight: 400;
        color: var(--text-muted);
        max-width: 600px;
        width: 100%;
        margin: 0 auto;
        line-height: 1.6;
        text-align: center;
        padding: 0 1rem;
        box-sizing: border-box;
    }
    
    /* Glass cards */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 1.75rem;
        box-shadow: 0 8px 32px var(--glass-shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }
    
    .card-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-white);
        margin-bottom: 1.25rem;
    }
    
    .card-title-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 12px;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    /* Status panel */
    .status-panel {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(34, 211, 238, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    /* Status header row - contains title and badge together */
    .status-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .status-header-row .card-title {
        margin-bottom: 0;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 1rem;
        border-radius: 100px;
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        white-space: nowrap;
        flex-shrink: 0;
    }
    
    .status-idle {
        background: rgba(100, 116, 139, 0.15);
        border: 1px solid rgba(100, 116, 139, 0.3);
        color: var(--text-dim);
    }
    
    .status-running {
        background: rgba(34, 211, 238, 0.15);
        border: 1px solid rgba(34, 211, 238, 0.3);
        color: var(--accent-cyan);
        animation: statusPulse 2s infinite;
    }
    
    .status-complete {
        background: rgba(52, 211, 153, 0.15);
        border: 1px solid rgba(52, 211, 153, 0.3);
        color: var(--accent-emerald);
    }
    
    @keyframes statusPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(34, 211, 238, 0); }
    }
    
    .config-info {
        margin-top: 1.25rem;
        padding-top: 1rem;
        border-top: 1px solid var(--glass-border);
    }
    
    .config-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 0;
    }
    
    .config-label {
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .config-value {
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-light);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        color: white;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:disabled {
        background: rgba(100, 116, 139, 0.3);
        box-shadow: none;
        cursor: not-allowed;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        color: var(--text-white);
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        padding: 0.85rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        background: rgba(99, 102, 241, 0.05);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-dim);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-cyan), var(--accent-tertiary));
        border-radius: 100px;
    }
    
    /* Results section */
    .results-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .results-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-white);
    }
    
    .results-badge {
        background: linear-gradient(135deg, var(--accent-emerald), #059669);
        color: white;
        font-family: 'Fira Code', monospace;
        font-size: 0.7rem;
        font-weight: 500;
        padding: 0.35rem 0.75rem;
        border-radius: 100px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 14px;
        padding: 0.35rem;
        gap: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: var(--text-muted);
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        padding: 0.75rem 1.25rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-light);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    
    /* Report content styling */
    .stMarkdown {
        color: var(--text-light);
    }
    
    .stMarkdown h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: var(--accent-cyan);
        border-bottom: 2px solid var(--glass-border);
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    .stMarkdown h2 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: var(--accent-primary);
        margin-top: 1.25rem;
    }
    
    .stMarkdown h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        color: var(--text-white);
    }
    
    .stMarkdown p, .stMarkdown li {
        font-family: 'Outfit', sans-serif;
        line-height: 1.7;
        color: var(--text-muted);
    }
    
    .stMarkdown strong {
        color: var(--text-light);
    }
    
    .stMarkdown code {
        background: rgba(99, 102, 241, 0.15);
        color: var(--accent-cyan);
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-family: 'Fira Code', monospace;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-emerald), #059669);
        border: none;
        box-shadow: 0 4px 16px rgba(52, 211, 153, 0.3);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 24px rgba(52, 211, 153, 0.4);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--glass-border);
        border-radius: 100px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }
    
    /* Footer */
    .sidebar-footer {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-top: auto;
        border-top: 1px solid var(--glass-border);
    }
    
    .footer-text {
        font-family: 'Fira Code', monospace;
        font-size: 0.65rem;
        color: var(--text-dim);
        line-height: 1.8;
    }
    
    .footer-link {
        color: var(--accent-primary);
        text-decoration: none;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent-primary) transparent transparent transparent;
    }
    
    /* Task progress tracker */
    .task-tracker {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .task-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--glass-border);
    }
    
    .task-item:last-child {
        border-bottom: none;
    }
    
    .task-number {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--accent-primary);
    }
    
    .task-number.complete {
        background: var(--accent-emerald);
        color: white;
    }
    
    .task-number.active {
        background: var(--accent-cyan);
        color: var(--bg-dark);
        animation: taskPulse 1.5s infinite;
    }
    
    @keyframes taskPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .task-name {
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem;
        color: var(--text-muted);
    }
    
    .task-name.active {
        color: var(--text-white);
        font-weight: 500;
    }
    
    .task-name.complete {
        color: var(--accent-emerald);
    }
</style>
""", unsafe_allow_html=True)



def get_ollama_models():
    """Fetch available models from Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models if models else []
        return []
    except requests.exceptions.RequestException:
        return []


def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "research_running": False,
        "research_complete": False,
        "current_task": "",
        "provider": "ollama",
        "selected_model": "",
        "api_key": "",
        "company_name": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """Render the enhanced sidebar"""
    with st.sidebar:
        # Logo section
        st.markdown("""
        <div class="sidebar-logo">
            <span class="sidebar-logo-icon">📊</span>
            <div class="sidebar-logo-text">FinResearch AI</div>
            <div class="sidebar-logo-subtitle">Intelligent Analysis</div>
        </div>
        """, unsafe_allow_html=True)
        
        # LLM Configuration Section
        st.markdown("""
        <div class="sidebar-section">
            <div class="section-header">
                <div class="section-icon">⚡</div>
                <div class="section-title">LLM Provider</div>
            </div>
        """, unsafe_allow_html=True)
        
        provider = st.selectbox(
            "Select Provider",
            ["ollama", "openai", "anthropic", "groq"],
            index=["ollama", "openai", "anthropic", "groq"].index(st.session_state.provider),
            key="provider_select",
            label_visibility="collapsed"
        )
        st.session_state.provider = provider
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Model Selection Section
        if provider == "ollama":
            ollama_connected = check_ollama_connection()
            ollama_models = get_ollama_models() if ollama_connected else []
            
            st.markdown("""
            <div class="sidebar-section">
                <div class="section-header">
                    <div class="section-icon">🦙</div>
                    <div class="section-title">Ollama Models</div>
                </div>
            """, unsafe_allow_html=True)
            
            if ollama_connected and ollama_models:
                selected_model = st.selectbox(
                    "Select Model",
                    ollama_models,
                    key="ollama_model_select",
                    label_visibility="collapsed"
                )
                st.session_state.selected_model = selected_model
                
                st.markdown(f"""
                <div class="connection-status">
                    <div class="status-dot"></div>
                    <span class="status-text">Connected to localhost:11434</span>
                </div>
                <div class="model-card">
                    <div class="model-name">{selected_model}</div>
                    <div class="model-meta">Local Instance • Ready</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="connection-status error">
                    <div class="status-dot error"></div>
                    <span class="status-text error">Ollama not connected</span>
                </div>
                """, unsafe_allow_html=True)
                st.info("💡 Run `ollama serve` to start Ollama")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            # Cloud provider section
            st.markdown(f"""
            <div class="sidebar-section">
                <div class="section-header">
                    <div class="section-icon">🔑</div>
                    <div class="section-title">{provider.upper()} Config</div>
                </div>
            """, unsafe_allow_html=True)
            
            api_key = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.api_key,
                placeholder=f"Enter {provider} API key...",
                key="api_key_input",
                label_visibility="collapsed"
            )
            st.session_state.api_key = api_key
            
            model_options = {
                "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
                "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            }
            
            selected_model = st.selectbox(
                "Model",
                model_options.get(provider, []),
                key="cloud_model_select",
                label_visibility="collapsed"
            )
            st.session_state.selected_model = selected_model
            
            if api_key:
                st.markdown(f"""
                <div class="connection-status">
                    <div class="status-dot"></div>
                    <span class="status-text">API Key configured</span>
                </div>
                <div class="model-card">
                    <div class="model-name">{selected_model}</div>
                    <div class="model-meta">{provider.upper()} • Cloud</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="connection-status error">
                    <div class="status-dot error"></div>
                    <span class="status-text error">API key required</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Research Agents Section
        st.markdown("""
        <div class="sidebar-section">
            <div class="section-header">
                <div class="section-icon">🤖</div>
                <div class="section-title">Research Team</div>
            </div>
            <div class="agent-grid">
                <div class="agent-item">
                    <div class="agent-icon research">🔬</div>
                    <div class="agent-info">
                        <div class="agent-name">Head of Research</div>
                        <div class="agent-role">Web Research & Strategy</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon analyst">📊</div>
                    <div class="agent-info">
                        <div class="agent-name">Financial Analyst</div>
                        <div class="agent-role">Financial Analysis</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon data">📈</div>
                    <div class="agent-info">
                        <div class="agent-name">Data Analyst</div>
                        <div class="agent-role">Market Analysis</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon writer">📝</div>
                    <div class="agent-info">
                        <div class="agent-name">Report Writer</div>
                        <div class="agent-role">Report Compilation</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div class="sidebar-footer">
            <div class="footer-text">
                Financial Research AI v1.0<br>
                Powered by <span class="footer-link">CrewAI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def run_research(company: str):
    """Run the research crew"""
    try:
        os.makedirs('output', exist_ok=True)
        
        llm_instance = create_llm(
            provider=st.session_state.provider,
            model=st.session_state.selected_model,
            api_key=st.session_state.api_key if st.session_state.provider != "ollama" else None
        )
        
        inputs = {
            "company": company,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        }
        
        research_crew = ResearchCrew(llm_instance=llm_instance)
        result = research_crew.crew().kickoff(inputs=inputs)
        
        return True, result
        
    except Exception as e:
        return False, str(e)


def read_output_file(filename: str) -> str:
    """Read content from output file"""
    filepath = Path("output") / filename
    if filepath.exists():
        return filepath.read_text()
    return ""


def main():
    """Main application"""
    init_session_state()
    render_sidebar()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">Financial Research AI</h1>
        <p class="main-subtitle">
            Comprehensive AI-powered financial analysis and research reports 
            generated by a team of specialized AI agents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content columns
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">
                <div class="card-title-icon">🔍</div>
                <span>Research Configuration</span>
            </div>
        """, unsafe_allow_html=True)
        
        company = st.text_input(
            "Company Name",
            placeholder="Enter company name (e.g., Apple, Microsoft, Tesla, NVIDIA)",
            key="company_input",
            label_visibility="collapsed"
        )
        st.session_state.company_name = company
        
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2, gap="medium")
        
        with col_btn1:
            can_start = (
                company and 
                not st.session_state.research_running and
                st.session_state.selected_model and
                (st.session_state.provider == "ollama" or st.session_state.api_key)
            )
            
            if st.button("🚀 Start Research", disabled=not can_start, key="start_btn", use_container_width=True):
                st.session_state.research_running = True
                st.session_state.research_complete = False
                st.rerun()
        
        with col_btn2:
            if st.button("🗑️ Clear Results", key="clear_btn", use_container_width=True):
                st.session_state.research_complete = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Determine status indicator
        if st.session_state.research_running:
            status_badge = '<span class="status-indicator status-running">⟳ Processing</span>'
        elif st.session_state.research_complete:
            status_badge = '<span class="status-indicator status-complete">✓ Complete</span>'
        else:
            status_badge = '<span class="status-indicator status-idle">○ Ready</span>'
        
        st.markdown(f"""
        <div class="glass-card">
            <div class="status-panel">
                <div class="status-header-row">
                    <div class="card-title">
                        <div class="card-title-icon">📡</div>
                        <span>Status</span>
                    </div>
                    {status_badge}
                </div>
                <div class="config-info">
                    <div class="config-row">
                        <span class="config-label">Provider</span>
                        <span class="config-value">{st.session_state.provider.upper()}</span>
                    </div>
                    <div class="config-row">
                        <span class="config-label">Model</span>
                        <span class="config-value">{st.session_state.selected_model or '—'}</span>
                    </div>
                    <div class="config-row">
                        <span class="config-label">Target</span>
                        <span class="config-value">{st.session_state.company_name or '—'}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Research execution
    if st.session_state.research_running:
        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <div class="card-title">
                <div class="card-title-icon">⚡</div>
                <span>Research in Progress</span>
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.info("🔄 Initializing research agents...")
        
        success, result = run_research(company)
        
        if success:
            progress_bar.progress(100)
            status_text.success("✅ Research completed successfully!")
            st.session_state.research_complete = True
        else:
            status_text.error(f"❌ Error: {result}")
        
        st.session_state.research_running = False
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        time.sleep(1)
        st.rerun()
    
    # Display results
    if st.session_state.research_complete:
        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <div class="results-header">
                <span class="results-title">📋 Research Results</span>
                <span class="results-badge">Complete</span>
            </div>
        """, unsafe_allow_html=True)
        
        tabs = st.tabs([
            "📊 Final Report",
            "🔬 Research",
            "📈 Company",
            "⚠️ Risk",
            "🌍 Market"
        ])
        
        with tabs[0]:
            report_content = read_output_file("report.md")
            if report_content:
                st.markdown(report_content)
            else:
                st.info("Report not yet generated")
        
        with tabs[1]:
            content = read_output_file("financial_research.md")
            if content:
                st.markdown(content)
            else:
                st.info("Not yet generated")
        
        with tabs[2]:
            content = read_output_file("company_analysis.md")
            if content:
                st.markdown(content)
            else:
                st.info("Not yet generated")
        
        with tabs[3]:
            content = read_output_file("risk_assessment.md")
            if content:
                st.markdown(content)
            else:
                st.info("Not yet generated")
        
        with tabs[4]:
            content = read_output_file("market_analysis.md")
            if content:
                st.markdown(content)
            else:
                st.info("Not yet generated")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download section
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        
        report_content = read_output_file("report.md")
        if report_content:
            col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
            with col_dl2:
                st.download_button(
                    label="📥 Download Full Report",
                    data=report_content,
                    file_name=f"{st.session_state.company_name}_financial_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )


if __name__ == "__main__":
    main()
