import streamlit as st
import pandas as pd
from typing import List
import os

# Import the query engine (assuming it's in a file called greek_query_engine.py)
from engine import create_query_engine, GreekQueryEngine

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
            'Sentence ID': word.sentence_id,
            'Document URN': word.urn
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
    
def create_engine_from_files(urns: List[str]):
    this_dir = os.path.dirname(__file__)
    
    all_files = {}
    
    with st.spinner("Loading XML data..."):
        for urn in urns:
            doc_path = os.path.join(this_dir, "data", "xml", f"{urn}.xml")
            try:
                with open(doc_path, 'rb') as doc:
                    xml_content = doc.read().decode('utf-8')
                    all_files[urn] = xml_content
            except: 
                st.error(f"Error opening document with urn {urn}.")  
                #return False
        
    st.success("XML data loaded successfully!")
    st.info("Ready to execute queries.")
    return create_query_engine(all_files)

@st.cache_resource    
def get_query_engine(urns):
    return create_engine_from_files(urns)

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
        
    #QUERY EXECUTION
    if search_button and query:
        if 'selected_urns' not in st.session_state or not st.session_state.get('engine_loaded', False):
            st.error("No data loaded. Have you selected and confirmed your document list?")
        else:
            try:
                print("attempting to execute query")
                with st.spinner("Executing query..."):
                    query_engine = get_query_engine(st.session_state.selected_urns)
                    results = query_engine.query(query)
                
                st.session_state.current_results = results
                st.session_state.current_query = query
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
                st.info("Please check your query syntax and try again.")

    #DISPLAY RESULTS
    if 'current_results' in st.session_state and st.session_state.current_results:
        results = st.session_state.current_results
        query = st.session_state.current_query
        total_results = len(results)
        
        st.success(f"Found {total_results} results for query: `{query}`")
        if total_results > 50000:
            st.warning(f"⚠️ Very large result set ({total_results:,} results). Consider refining your query for better performance.")
        
        if st.button("🗑️ Clear Results"):
            del st.session_state.current_results
            del st.session_state.current_query
            st.rerun()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            results_per_page = st.selectbox("Results per page:", [50, 100, 500, 1000], index=1, key="results_per_page")
            total_pages = (total_results + results_per_page - 1) // results_per_page
        with col2:
            page = st.number_input(
                f"Page (1-{total_pages}):",
                min_value=1,
                max_value=total_pages,
                value=1,
                key="current_page"
            )
        
        #get slice sizes, then show results
        start_idx = (page - 1) * results_per_page
        end_idx = min(start_idx + results_per_page, total_results)
        
        st.info(f"Showing results {start_idx + 1}-{end_idx} of {total_results}")
        df_results = format_word_results(results[start_idx:end_idx])
        st.dataframe(df_results, use_container_width=True)
        
        #DATA DOWNLOAD
        #current page and full results - WILL BE USEFUL WHEN SENTENCES ARE ADDED
        col1, col2 = st.columns(2)
        with col1:
            csv_page = df_results.to_csv(index=False)
            st.download_button(
                label=f"📥 Download Current Page as CSV ({len(df_results)} results)",
                data=csv_page,
                file_name=f"greek_query_results_page_{page}_{query.replace(' ', '_')}.csv",
                mime="text/csv",
                key="download_page"
            )
        
        with col2:
            if total_results > 10000:
                st.warning(f"⚠️ Full export contains {total_results} results - may be very large!")
            
            if st.button("Prepare Full CSV Download", key="prepare_csv"):
                with st.spinner("Preparing full results..."):
                    df_full = format_word_results(results)
                    csv_full = df_full.to_csv(index=False)
                    st.session_state.full_csv_data = csv_full
                    st.session_state.full_csv_ready = True
            
            if st.session_state.get('full_csv_ready', False):
                st.download_button(
                    label=f"📥 Download All Results as CSV ({total_results} results)",
                    data=st.session_state.full_csv_data,
                    file_name=f"greek_query_results_full_{query.replace(' ', '_')}.csv",
                    mime="text/csv",
                    key="download_full"
                )
                
    elif 'current_results' in st.session_state and not st.session_state.current_results:
        st.warning("No results found for your last query.")
        
    #DATA HANDLING
    st.markdown("---")
    st.header("Data Management")

    df = pd.read_csv("matched_urns.csv")
    df["Display Label"] = df.apply(lambda row: f"{row['URN']} {row['Author']}, {row['Title']}", axis=1)
    
    container = st.container()
    all = st.checkbox("Select all")
    if all:
        selected_labels = container.multiselect("Select document(s):", df["Display Label"].tolist(), df["Display Label"].tolist())
    else:
        selected_labels = container.multiselect("Select document(s):", df["Display Label"].tolist())
        
    selected_rows = df[df["Display Label"].isin(selected_labels)]
    st.write("Current selection:")
    st.dataframe(selected_rows)
    confirmed_selection = st.button("Confirm Selection")
    
    urns = []
    if confirmed_selection and not selected_rows.empty:
        urns = [urn for urn in selected_rows["URN"]]
        st.session_state.selected_urns = urns #might need to convert to tuple
        st.session_state.engine_loaded = True
        st.success("URNs successfully saved.")
        print("query engine created or loaded")            
    if selected_rows.empty:
        st.info("Please select one or more documents")
        st.session_state.selected_urns =[]
        st.session_state.engine_loaded = False

if __name__ == "__main__":
    main()