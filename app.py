import streamlit as st
import nbformat
import os
import re

# Set page config
st.set_page_config(
    page_title="Anthropic Prompt Engineering Tutorial",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Card styling */
    .stCard {
        padding: 1rem;
        border-radius: 0.5rem;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .stCard:hover {
        transform: translateY(-5px);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .stCard {
            background: #2d2d2d;
        }
    }
    
    /* Grid layout */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        padding: 1rem;
    }
    
    /* Header styling */
    .header-container {
        padding: 1rem;
        margin-bottom: 2rem;
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header-text {
        text-align: center;
    }
    .header-text h1 {
        margin-bottom: 0.5rem;
    }
    
    /* Code block styling */
    .stCodeBlock {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 0.5rem;
        background: #f8f9fa;
    }
    
    @media (prefers-color-scheme: dark) {
        .header-container {
            background: #2d2d2d;
        }
        .stCodeBlock {
            background: #1e1e1e;
        }
    }
    </style>
""", unsafe_allow_html=True)

def create_card(title, description, icon="📚"):
    return f"""
    <div class="stCard">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """

def read_notebook(file_path):
    """Read and parse a Jupyter notebook."""
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    return notebook

def display_notebook_content(notebook):
    """Display notebook content in a structured way."""
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            st.markdown(cell.source)
        elif cell.cell_type == "code":
            # Show code directly
            st.code(cell.source, language="python")
            
            # Show outputs if any
            if hasattr(cell, 'outputs') and cell.outputs:
                for output in cell.outputs:
                    if 'text' in output:
                        st.text(output.text)
                    elif 'data' in output:
                        if 'text/plain' in output.data:
                            st.text(output.data['text/plain'])
                        if 'image/png' in output.data:
                            st.image(output.data['image/png'])

def search_notebooks(notebooks, search_query):
    """Search through notebooks for matching content."""
    results = []
    for notebook in notebooks:
        try:
            content = read_notebook(notebook)
            text_content = " ".join(cell.source.lower() for cell in content.cells)
            if search_query.lower() in text_content:
                results.append(notebook)
        except Exception:
            continue
    return results

def main():
    # Header
    st.markdown("""
        <div class="header-container">
            <div class="header-text">
                <h1>Anthropic Prompt Engineering Tutorial</h1>
                <p>Created by <a href="https://www.linkedin.com/in/bettercallmanav/">Manav</a> | 
                Source: <a href="https://github.com/anthropics/courses">Anthropic Courses</a></p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Get list of notebooks
    tutorial_path = "prompt_engineering_interactive_tutorial/Anthropic 1P"
    notebooks = sorted([f for f in os.listdir(tutorial_path) if f.endswith('.ipynb')])
    
    # Initialize session state for tracking current lesson
    if 'selected_notebook' not in st.session_state:
        st.session_state.selected_notebook = None
    
    # Sidebar content
    with st.sidebar:
        st.title("📚 Course Navigation")
        
        # Search functionality
        search_query = st.text_input("🔍 Search lessons", key="search")
        if search_query:
            notebooks = search_notebooks([os.path.join(tutorial_path, nb) for nb in notebooks], search_query)
        
        # Categorized navigation
        categories = {
            "Getting Started": [nb for nb in notebooks if nb.startswith("00_")],
            "Basic Concepts": [nb for nb in notebooks if any(nb.startswith(f"0{i}_") for i in range(1,6))],
            "Advanced Topics": [nb for nb in notebooks if any(nb.startswith(f"0{i}_") for i in range(6,10))],
            "Appendix": [nb for nb in notebooks if nb.startswith("10")]
        }
        
        for category, category_notebooks in categories.items():
            if category_notebooks:
                st.markdown(f"### {category}")
                for notebook in sorted(category_notebooks):
                    number, title = notebook.split('_', 1)[0], notebook.split('_', 1)[1].replace('.ipynb', '').replace('_', ' ')
                    
                    button_key = f"button_{notebook}"
                    is_current = st.session_state.selected_notebook == notebook
                    
                    if st.button(
                        f"{number} {title}",
                        key=button_key,
                        help=f"Go to {title}",
                        use_container_width=True
                    ):
                        st.session_state.selected_notebook = notebook
                        st.rerun()
    
    # Main content area
    if st.session_state.selected_notebook:
        selected_notebook = st.session_state.selected_notebook
        
        # Display current lesson title
        number, title = selected_notebook.split('_', 1)[0], selected_notebook.split('_', 1)[1].replace('.ipynb', '').replace('_', ' ')
        st.header(f"Lesson {number}: {title}", divider="rainbow")
        
        # Read and display notebook content
        notebook_path = os.path.join(tutorial_path, selected_notebook)
        try:
            notebook = read_notebook(notebook_path)
            display_notebook_content(notebook)
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1,3,1])
            current_index = notebooks.index(selected_notebook)
            
            with col1:
                if current_index > 0:
                    if st.button("← Previous Lesson", use_container_width=True):
                        st.session_state.selected_notebook = notebooks[current_index - 1]
                        st.rerun()
            
            with col3:
                if current_index < len(notebooks) - 1:
                    if st.button("Next Lesson →", use_container_width=True):
                        st.session_state.selected_notebook = notebooks[current_index + 1]
                        st.rerun()
        
        except Exception as e:
            st.error(f"Error loading notebook: {str(e)}")
    else:
        # Interactive homepage with cards
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        
        # Course Overview Card
        st.markdown(create_card(
            "Course Overview",
            "Learn the fundamentals and advanced techniques of prompt engineering with Claude.",
            "🎯"
        ), unsafe_allow_html=True)
        
        # Getting Started Card
        st.markdown(create_card(
            "Getting Started",
            "Begin with the basics and learn how to structure your prompts effectively.",
            "🚀"
        ), unsafe_allow_html=True)
        
        # Basic Concepts Card
        st.markdown(create_card(
            "Basic Concepts",
            "Master the fundamental concepts of prompt engineering.",
            "📖"
        ), unsafe_allow_html=True)
        
        # Advanced Topics Card
        st.markdown(create_card(
            "Advanced Topics",
            "Dive deep into advanced prompt engineering techniques.",
            "🔬"
        ), unsafe_allow_html=True)
        
        # Practice Exercises Card
        st.markdown(create_card(
            "Practice Exercises",
            "Apply your knowledge with hands-on exercises and examples.",
            "✍️"
        ), unsafe_allow_html=True)
        
        # Resources Card
        st.markdown(create_card(
            "Additional Resources",
            "Explore supplementary materials and documentation.",
            "📚"
        ), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🚀 Getting Started
        Select a lesson from the sidebar to begin your learning journey.
        
        ### 📚 Course Source
        All course content is from the [Anthropic Courses Repository](https://github.com/anthropics/courses).
        """)

if __name__ == "__main__":
    main()
