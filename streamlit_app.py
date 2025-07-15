import streamlit as st
import pandas as pd
from typing import List

# Import the query engine (assuming it's in a file called greek_query_engine.py)
from engine import create_query_engine

def format_word_results(words: List) -> pd.DataFrame:
    """Format query results into a DataFrame for display."""
    if not words:
        return pd.DataFrame()
    
    data = []
    for word in words:
        data.append({
            'Form': word.form,
            'Lemma': word.lemma,
            'Part of Speech': word.part_of_speech or '',
            'Case': word.case or '',
            'Number': word.number or '',
            'Tense': word.tense or '',
            'Mood': word.mood or '',
            'Voice': word.voice or '',
            'Relation': word.relation or '',
            'Sentence ID': word.sentence_id
        })
    
    return pd.DataFrame(data)

def create_query_examples():
    """Create example queries for the user interface."""
    return {
        "Basic Lemma Search": "μῆνις",
        "Accusative Case": ":accusative",
        "Third Person Singular Verbs": ":third:singular:verb",
        "Infinitive Verbs": ":infinitive:verb",
        "Genitive Case": ":genitive",
        "Nouns": ":noun",
        "Adjectives modifying nouns": ":noun > :adjective[relation=ATR]",
        "Root words (main clauses)": ":root",
        "Conditionals": "εἰ[relation=AuxC]",
        "Substantival infinitives as subjects": ":infinitive:verb[relation=SBJ]",
        "Genitive absolutes": ":genitive[relation=SBJ]",
        "Indicative verbs with accusative objects": ":verb:indicative:root > :accusative[relation=OBJ]"
    }

def main():
    st.set_page_config(
        page_title="Greek Text Query Engine",
        page_icon="🏛️",
        layout="wide"
    )
    
    st.title("🏛️ Perseus Treebank Query Engine")
    st.markdown("Search ancient Greek texts using CSS-like selectors with linguistic features")
    st.markdown("A Python/Streamlit implementation of Nick Kallen's pseudw: **https://github.com/nkallen/pseudw**")
    
    # Sidebar for help and examples
    with st.sidebar:
        st.header("Query Examples")
        examples = create_query_examples()
        
        selected_example = st.selectbox(
            "Choose an example query:",
            list(examples.keys())
        )
        
        if st.button("Use Example"):
            st.session_state.query = examples[selected_example]
        
        st.markdown("---")
        st.markdown("### Query Syntax Help")
        st.markdown("""
        **Basic Searches:**
        - `μῆνις` - Find lemma
        - `:accusative` - Find accusative case
        - `:verb` - Find verbs
        
        **Combined Features:**
        - `:third:singular:verb` - Third person singular verbs
        - `αἰτέω:first:singular:present` - Specific lemma with features
        
        **Attribute Selectors:**
        - `[form=φθογγὴν]` - Specific word form
        - `[relation=AuxC]` - Specific syntactic relation
        
        **Relationships:**
        - `μῆνις > :adjective[relation=ATR]` - Adjectives modifying μῆνις
        - `φίλος + γάρ + εἰμί` - Adjacent words
        - `φίλος ~ εἰμί` - Word order (not necessarily adjacent)
        
        **Multiple Selectors:**
        - `selector1 selector2` - Both selectors
        """)
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter your query:",
            value=st.session_state.get('query', ''),
            placeholder="e.g., :accusative or μῆνις > :adjective[relation=ATR]",
            key="query"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary")

    # should_execute = False
    # if search_button and query:
    #     should_execute = True
    #elif query and 'last_query' in st.session_state and st.session_state.last_query != query:
        # Auto-execute when query changes (optional)
        #should_execute = True   
         
    # Execute query
    if search_button and query:
        if st.session_state.query_engine is None:
            st.error("No data loaded. Please load Perseus Treebank XML data first.")
            return
        
        try:
            with st.spinner("Executing query..."):
                results = st.session_state.query_engine.query(query)
            
            if results:
                st.success(f"Found {len(results)} results")
                
                # Display results in a table
                df = format_word_results(results)
                st.dataframe(df, use_container_width=True)
                
                # Show detailed results
                # with st.expander("Detailed Results"):
                #     for i, word in enumerate(results, 1):
                #         st.markdown(f"**Result {i}:**")
                #         col1, col2, col3 = st.columns(3)
                        
                #         with col1:
                #             st.write(f"**Form:** {word.form}")
                #             st.write(f"**Lemma:** {word.lemma}")
                #             st.write(f"**Part of Speech:** {word.part_of_speech or 'N/A'}")
                        
                #         with col2:
                #             st.write(f"**Case:** {word.case or 'N/A'}")
                #             st.write(f"**Number:** {word.number or 'N/A'}")
                #             st.write(f"**Tense:** {word.tense or 'N/A'}")
                        
                #         with col3:
                #             st.write(f"**Mood:** {word.mood or 'N/A'}")
                #             st.write(f"**Voice:** {word.voice or 'N/A'}")
                #             st.write(f"**Relation:** {word.relation or 'N/A'}")
                        
                #         st.markdown("---")
                
                # Export functionality
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"greek_query_results_{query.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.warning("No results found for your query.")
                
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            st.info("Please check your query syntax and try again.")
    
    # Data upload section
    st.markdown("---")
    st.header("Data Management")
    st.markdown("Please provide XML data below. As of right now, files must be uploaded.")
    
    uploaded_file = st.file_uploader(
        "Upload Perseus Treebank XML file",
        type=['xml'],
        help="Upload your Perseus Treebank XML data to search"
    )
    
    if uploaded_file is not None:
        try:
            xml_content = uploaded_file.read().decode('utf-8')
            with st.spinner("Processing XML data..."):
                st.session_state.query_engine = create_query_engine(xml_content)
                st.success("XML data loaded successfully!")
                st.info("Ready to execute queries.")
        except Exception as e:
            st.error(f"Error loading XML file: {str(e)}")

if __name__ == "__main__":
    main()