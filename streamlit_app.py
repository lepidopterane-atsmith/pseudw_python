import streamlit as st
import pandas as pd
from typing import List
import os
from tqdm import tqdm

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
            'Sentence ID': word.sentence_id,
            'Word ID': word.id,
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
    
caught_urns = ["0284-047","1799-01"]
all_urns = ['0001-001', '0002-004', '0003-001', '0003-002', '0005-001', '0005-002', '0005-005', '0006-007', '0006-008', '0006-009', '0006-010', '0006-011', '0006-012', '0006-013', '0006-014', '0006-015', '0006-016', '0006-017', '0006-018', '0006-019', '0006-031', '0007-001', '0007-002', '0007-003', '0007-004', '0007-005', '0007-006', '0007-007', '0007-008', '0007-009', '0007-010', '0007-011', '0007-012', '0007-013', '0007-014', '0007-015', '0007-016', '0007-017', '0007-018', '0007-019', '0007-020', '0007-021', '0007-022', '0007-023', '0007-024', '0007-025', '0007-026', '0007-027', '0007-028', '0007-029', '0007-030', '0007-031', '0007-032', '0007-033', '0007-034', '0007-035', '0007-036', '0007-037', '0007-038', '0007-039', '0007-040', '0007-041', '0007-042', '0007-043', '0007-044', '0007-045', '0007-046', '0007-047', '0007-048', '0007-049', '0007-050', '0007-053', '0007-054', '0007-055', '0007-056', '0007-057', '0007-058', '0007-059', '0007-060', '0007-061', '0007-062', '0007-063', '0007-064', '0007-065', '0007-066', '0007-072', '0007-073', '0007-074', '0007-075', '0007-081', '0007-082', '0007-083', '0007-085', '0007-088', '0008-001', '0009-002', '0010-001', '0010-002', '0010-003', '0010-004', '0010-005', '0010-006', '0010-007', '0010-008', '0010-009', '0010-010', '0010-011', '0010-012', '0010-013', '0010-014', '0010-015', '0010-016', '0010-017', '0010-018', '0010-019', '0010-020', '0010-021', '0010-022', '0010-023', '0010-024', '0010-025', '0010-026', '0010-027', '0010-028', '0010-029', '0010-030', '0011-001', '0011-002', '0011-003', '0011-004', '0011-005', '0011-006', '0011-007', '0011-008', '0012-001', '0012-002', '0012-003', '0013-001', '0013-002', '0013-003', '0013-004', '0013-005', '0013-006', '0013-007', '0013-009', '0013-010', '0013-011', '0013-012', '0013-013', '0013-014', '0013-015', '0013-016', '0013-017', '0013-018', '0013-019', '0013-020', '0013-021', '0013-022', '0013-023', '0013-024', '0013-025', '0013-026', '0013-027', '0013-028', '0013-029', '0013-030', '0013-031', '0013-032', '0013-033', '0014-001', '0014-002', '0014-003', '0014-004', '0014-005', '0014-006', '0014-007', '0014-008', '0014-009', '0014-010', '0014-011', '0014-012', '0014-013', '0014-014', '0014-015', '0014-016', '0014-017', '0014-018', '0014-019', '0014-020', '0014-021', '0014-022', '0014-023', '0014-024', '0014-025', '0014-026', '0014-027', '0014-028', '0014-029', '0014-030', '0014-031', '0014-032', '0014-033', '0014-034', '0014-035', '0014-036', '0014-037', '0014-038', '0014-039', '0014-040', '0014-041', '0014-042', '0014-043', '0014-044', '0014-045', '0014-046', '0014-047', '0014-048', '0014-049', '0014-050', '0014-051', '0014-052', '0014-053', '0014-054', '0014-055', '0014-056', '0014-057', '0014-058', '0014-059', '0014-060', '0014-061', '0015-001', '0016-001', '0017-001', '0017-002', '0017-003', '0017-004', '0017-005', '0017-006', '0017-007', '0017-008', '0017-009', '0017-010', '0017-011', '0017-012', '0019-001', '0019-002', '0019-003', '0019-004', '0019-005', '0019-006', '0019-007', '0019-008', '0019-009', '0019-010', '0019-011', '0020-001', '0020-002', '0020-003', '0022-006', '0023-001', '0024-001', '0026-001', '0026-002', '0026-003', '0027-001', '0027-002', '0027-003', '0027-004', '0028-001', '0028-002', '0028-003', '0028-004', '0028-005', '0028-006', '0029-004', '0029-005', '0029-006', '0030-001', '0030-002', '0030-003', '0030-004', '0030-005', '0030-006', '0032-001', '0032-002', '0032-003', '0032-004', '0032-005', '0032-006', '0032-007', '0032-008', '0032-009', '0032-010', '0032-011', '0032-012', '0032-013', '0032-014', '0033-001', '0033-002', '0033-003', '0033-004', '0034-001', '0035-001', '0035-002', '0035-003', '0035-004', '0035-005', '0035-006', '0036-001', '0036-002', '0036-003', '0057-001', '0057-002', '0057-003', '0057-004', '0057-006', '0057-007', '0057-008', '0057-009', '0057-010', '0057-011', '0057-012', '0057-013', '0057-014', '0057-015', '0057-016', '0057-017', '0057-018', '0057-019', '0057-020', '0057-021', '0057-022', '0057-023', '0057-024', '0057-025', '0057-027', '0057-028', '0057-029', '0057-030', '0057-031', '0057-032', '0057-034', '0057-035', '0057-036', '0057-038', '0057-039', '0057-040', '0057-041', '0057-042', '0057-043', '0057-044', '0057-045', '0057-046', '0057-047', '0057-048', '0057-049', '0057-050', '0057-051', '0057-052', '0057-053', '0057-054', '0057-055', '0057-056', '0057-057', '0057-058', '0057-059', '0057-060', '0057-061', '0057-062', '0057-063', '0057-064', '0057-065', '0057-066', '0057-067', '0057-068', '0057-069', '0057-070', '0057-071', '0057-072', '0057-073', '0057-074', '0057-075', '0057-076', '0057-077', '0057-078', '0057-079', '0057-081', '0057-082', '0057-083', '0057-084', '0057-085', '0057-086', '0057-087', '0057-089', '0057-092', '0057-093', '0057-094', '0057-095', '0057-096', '0057-099', '0057-100', '0057-101', '0057-102', '0057-103', '0057-107', '0057-111', '0057-114', '0058-001', '0059-001', '0059-002', '0059-003', '0059-004', '0059-005', '0059-006', '0059-007', '0059-008', '0059-009', '0059-010', '0059-011', '0059-012', '0059-013', '0059-014', '0059-015', '0059-016', '0059-017', '0059-018', '0059-019', '0059-020', '0059-021', '0059-022', '0059-023', '0059-024', '0059-025', '0059-026', '0059-027', '0059-028', '0059-029', '0059-030', '0059-031', '0059-032', '0059-033', '0059-034', '0059-035', '0059-036', '0059-037', '0059-039', '0060-001', '0061-010', '0062-001', '0062-002', '0062-003', '0062-004', '0062-005', '0062-006', '0062-007', '0062-008', '0062-009', '0062-010', '0062-011', '0062-012', '0062-013', '0062-014', '0062-015', '0062-016', '0062-017', '0062-018', '0062-019', '0062-020', '0062-021', '0062-022', '0062-023', '0062-024', '0062-025', '0062-026', '0062-027', '0062-028', '0062-029', '0062-030', '0062-031', '0062-032', '0062-033', '0062-034', '0062-035', '0062-036', '0062-037', '0062-038', '0062-039', '0062-040', '0062-041', '0062-042', '0062-043', '0062-044', '0062-045', '0062-046', '0062-047', '0062-048', '0062-049', '0062-050', '0062-051', '0062-052', '0062-053', '0062-054', '0062-055', '0062-056', '0062-057', '0062-058', '0062-059', '0062-060', '0062-061', '0062-062', '0062-063', '0062-064', '0062-065', '0062-066', '0062-067', '0062-068', '0062-069', '0062-070', '0062-071', '0064-001', '0067-001', '0074-001', '0074-002', '0074-003', '0074-004', '0074-005', '0074-006', '0081-001', '0081-002', '0081-003', '0081-004', '0081-005', '0081-006', '0081-008', '0081-009', '0081-010', '0081-011', '0081-012', '0081-015', '0085-001', '0085-002', '0085-003', '0085-004', '0085-005', '0085-006', '0085-007', '0085-010', '0086-001', '0086-002', '0086-003', '0086-006', '0086-008', '0086-009', '0086-010', '0086-013', '0086-014', '0086-015', '0086-016', '0086-017', '0086-018', '0086-020', '0086-021', '0086-024', '0086-025', '0086-026', '0086-029', '0086-034', '0086-035', '0086-037', '0086-038', '0086-040', '0086-041', '0086-042', '0086-043', '0086-044', '0086-045', '0086-054', '0087-004', '0093-009', '0094-002', '0099-001', '0131-001', '0137-001', '0141-002', '0146-001', '0165-001', '0174-001', '0186-005', '0198-001', '0199-001', '0199-002', '0199-009', '0208-001', '0211-002', '0215-002', '0216-002', '0218-002', '0219-002', '0220-002', '0221-004', '0232-003', '0237-004', '0239-003', '0245-002', '0255-002', '0261-003', '0265-003', '0267-003', '0268-002', '0284-001', '0284-002', '0284-003', '0284-004', '0284-005', '0284-006', '0284-007', '0284-008', '0284-009', '0284-010', '0284-011', '0284-012', '0284-013', '0284-014', '0284-015', '0284-016', '0284-017', '0284-018', '0284-019', '0284-020', '0284-021', '0284-022', '0284-023', '0284-024', '0284-025', '0284-026', '0284-027', '0284-028', '0284-029', '0284-030', '0284-031', '0284-032', '0284-033', '0284-034', '0284-035', '0284-036', '0284-037', '0284-038', '0284-039', '0284-040', '0284-041', '0284-042', '0284-043', '0284-044', '0284-045', '0284-046', '0284-047', '0284-048', '0284-049', '0284-050', '0284-051', '0284-052', '0284-053', '0284-054', '0284-055', '0284-056', '0288-003', '0341-002', '0357-001', '0358-001', '0358-002', '0358-004', '0358-005', '0361-001', '0385-001', '0487-008', '0525-001', '0526-001', '0526-002', '0526-003', '0526-004', '0532-001', '0533-003', '0533-004', '0533-015', '0533-016', '0533-017', '0533-018', '0533-019', '0533-020', '0535-001', '0540-001', '0540-002', '0540-003', '0540-004', '0540-005', '0540-006', '0540-007', '0540-008', '0540-009', '0540-010', '0540-011', '0540-012', '0540-013', '0540-014', '0540-015', '0540-016', '0540-017', '0540-018', '0540-019', '0540-020', '0540-021', '0540-022', '0540-023', '0540-024', '0540-025', '0540-026', '0540-027', '0540-028', '0540-029', '0540-030', '0540-031', '0540-032', '0540-033', '0540-034', '0541-044', '0543-001', '0545-001', '0545-002', '0545-003', '0548-001', '0548-002', '0551-002', '0551-003', '0551-004', '0551-005', '0551-006', '0551-007', '0551-008', '0551-009', '0551-010', '0551-011', '0551-012', '0551-013', '0551-014', '0551-017', '0552-001', '0552-002', '0552-003', '0552-004', '0552-005', '0552-006', '0552-007', '0552-009', '0552-010', '0552-011', '0552-012', '0552-013', '0554-001', '0555-001', '0555-002', '0555-003', '0555-005', '0555-006', '0555-007', '0555-008', '0556-001', '0557-001', '0557-002', '0557-003', '0559-001', '0559-002', '0559-004', '0559-005', '0559-006', '0559-007', '0559-010', '0559-011', '0559-012', '0559-014', '0560-001', '0561-001', '0562-001', '0568-002', '0570-002', '0591-001', '0591-002', '0592-001', '0592-002', '0592-003', '0592-004', '0592-005', '0593-001', '0593-002', '0606-001', '0613-001', '0614-001', '0627-001', '0627-002', '0627-003', '0627-004', '0627-005', '0627-006', '0627-007', '0627-008', '0627-009', '0627-010', '0627-011', '0627-012', '0627-013', '0627-014', '0627-015', '0627-016', '0627-017', '0627-018', '0627-019', '0627-020', '0627-021', '0627-022', '0627-023', '0627-025', '0627-026', '0627-027', '0627-028', '0627-029', '0627-030', '0627-031', '0627-032', '0627-033', '0627-035', '0627-036', '0627-037', '0627-038', '0627-039', '0627-040', '0627-041', '0627-042', '0627-043', '0627-045', '0627-046', '0627-047', '0627-048', '0627-049', '0627-050', '0627-051', '0627-052', '0627-053', '0627-055', '0631-002', '0632-005', '0638-001', '0638-003', '0638-004', '0638-005', '0638-006', '0638-007', '0638-009', '0641-001', '0648-001', '0653-001', '0653-002', '0655-001', '0671-001', '0679-001', '0708-001', '0719-001', '0719-002', '0719-003', '0719-004', '0732-001', '0732-011', '0732-012', '0751-034', '1126-003', '1181-001', '1205-001', '1205-002', '1210-001', '1210-002', '1216-001', '1252-002', '1271-001', '1271-002', '1274-002', '1296-001', '1311-001', '1337-003', '1342-002', '1355-002', '1389-001', '1391-001', '1405-001', '1431-003', '1487-001', '1487-002', '1533-001', '1556-002', '1577-001', '1600-001', '1604-002', '1622-001', '1632-001', '1665-001', '1692-004', '1715-001', '1765-003', '1765-004', '1765-005', '1766-001', '1799-001', '1799-008', '1799-010', '1799-011', '1799-012', '1799-013', '1799-014', '1799-015', '1799-017', '2042-001', '2042-007', '2042-008', '2042-012', '2138-001', '2139-001']
# rerun this from main, see wot happens

def create_engine_from_files(urns: List[str]):
    print("urns in system: ", len(urns))
    this_dir = os.path.dirname(__file__)
    
    all_files = {}
    
    with st.spinner("Loading XML data..."):
        #print(urns) 
        for urn in urns:
            doc_path = os.path.join(this_dir, "data", "xml", f"{urn}.xml")
            if urn not in caught_urns:# and urn not in uncaught_urns:
                #print(urn)
                try:
                    with open(doc_path, 'rb') as doc: # < this is the misbehaving line
                        xml_content = doc.read().decode('utf-8')
                        all_files[urn] = xml_content
                except: 
                    #print("caught ",urn)
                    st.error(f"Error opening document with urn {urn}.")  # this doesnt really do exactly what we expected it to    

    # where do thread errors happen???
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
                    print("hi")
                    results = query_engine.query(query)
                    
                    
                    #for t in tqdm(range(1),desc="any%"):
                    #    print("hello")

                
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

def alternative_main():
    print("bonjour")
    create_engine_from_files(all_urns)

if __name__ == "__main__":
    main()