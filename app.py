import streamlit as st
import pandas as pd
import io

# Setup the web page
st.set_page_config(page_title="LNBTI Lead Routing", layout="centered")
st.title("🔄 LNBTI Lead Distribution System")
st.write("Upload your raw Meta or Website CSV. The system will evenly distribute the leads among the team.")

# Define the 7 team members
team_members = [
    "Agent 1", "Agent 2", "Agent 3", "Agent 4", 
    "Agent 5", "Agent 6", "Agent 7"
]

# Create the file uploader
uploaded_file = st.file_uploader("Upload Leads (CSV)", type=["csv"])

if uploaded_file is not None:
    # 1. Try standard UTF-8 encoding
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    # 2. If it fails, it's likely Facebook's UTF-16 format
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        # Facebook's UTF-16 files use tabs ('\t') instead of commas to separate columns
        df = pd.read_csv(uploaded_file, encoding='utf-16', sep='\t')
        
    # 3. Double-check: If everything is still mashed into 1 column, force it to split by tabs
    if len(df.columns) == 1:
        uploaded_file.seek(0)
        # Try UTF-8 with tabs just in case
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', sep='\t')
        except UnicodeDecodeError:
            pass # Keep the previous dataframe if this fails
            
    st.success(f"Successfully loaded {len(df)} leads!")
    
    # Check if the 'Programme' column exists to balance Computing vs Software Engineering equally
    if 'Programme' in df.columns:
        df['Assigned To'] = ""
        # Distribute evenly within each specific programme
        for prog in df['Programme'].unique():
            prog_mask = df['Programme'] == prog
            prog_count = prog_mask.sum()
            
            prog_assignments = [team_members[i % len(team_members)] for i in range(prog_count)]
            df.loc[prog_mask, 'Assigned To'] = prog_assignments
    else:
        # Standard round-robin if the Programme column isn't found
        assignments = [team_members[i % len(team_members)] for i in range(len(df))]
        df['Assigned To'] = assignments
    
    # Show a preview of the results
    st.write("### Preview of Assigned Leads")
    st.dataframe(df.head(10))
    
    # Create the downloadable file
    csv_buffer = io.StringIO()
    # Save the output back to standard UTF-8 with commas so Excel reads it easily
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    
    st.download_button(
        label="📥 Download Assigned Leads",
        data=csv_buffer.getvalue(),
        file_name="Distributed_Leads.csv",
        mime="text/csv"
    )
