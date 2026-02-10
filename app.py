import json
import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="JSON Flight Merger", layout="wide")

st.title("✈️ Flight JSON Merger")
st.write("Upload JSON files, categorise by `dataSource`, and export to Excel.")

st.sidebar.header("Upload JSON Files")

uploaded_files = st.sidebar.file_uploader(
    "Upload JSON files",
    type=["json"],
    accept_multiple_files=True
)

if st.button("🚀 Process Files") and uploaded_files:

    customs_transit = []
    customs_pax = []
    airline_file = []
    airways = []
    other = []

    with st.spinner("Processing JSON files..."):
        for file in uploaded_files:
            try:
                data = json.load(file)

                if isinstance(data, dict) and "flights" in data:
                    records = data["flights"]
                elif isinstance(data, list):
                    records = data
                else:
                    continue

                for record in records:
                    source = str(record.get("dataSource", "")).lower()
                    if source == "customstransit":
                        customs_transit.append(record)
                    elif source == "customspax":
                        customs_pax.append(record)
                    elif source == "airlinefile":
                        airline_file.append(record)
                    elif source == "airways":
                        airways.append(record)
                    else:
                        other.append(record)

            except json.JSONDecodeError:
                st.warning(f"Skipping invalid JSON file: {file.name}")

    df_transit = pd.DataFrame(customs_transit)
    df_pax = pd.DataFrame(customs_pax)
    df_airline = pd.DataFrame(airline_file)
    df_airways = pd.DataFrame(airways)
    df_other = pd.DataFrame(other)

    for df in [df_transit, df_pax, df_airline, df_airways]:
        for col in ["blocksDateTime", "scheduledDateTime", "actualDateTime"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    st.subheader("📊 Summary")
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("CustomsTransit", len(df_transit))
    col2.metric("CustomsPax", len(df_pax))
    col3.metric("AirlineFile", len(df_airline))
    col4.metric("Airways", len(df_airways))
    col5.metric("Other", len(df_other))

    st.subheader("⬇️ Download Excel")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        if not df_transit.empty:
            df_transit.to_excel(writer, sheet_name="CustomsTransit", index=False)
        if not df_pax.empty:
            df_pax.to_excel(writer, sheet_name="CustomsPax", index=False)
        if not df_airline.empty:
            df_airline.to_excel(writer, sheet_name="AirlineFile", index=False)
        if not df_airways.empty:
            df_airways.to_excel(writer, sheet_name="Airways", index=False)
        if not df_other.empty:
            df_other.to_excel(writer, sheet_name="Other", index=False)

    st.download_button(
        "Download merged_data.xlsx",
        data=output.getvalue(),
        file_name="merged_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload JSON files and click **Process Files**.")
