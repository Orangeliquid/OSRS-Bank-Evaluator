import streamlit as st

from app.database import init_db
from ui.bank_browser import display_bank_browser
from ui.item_compare import display_item_compare
from ui.snapshot_compare import display_snapshot_compare

st.set_page_config(page_title="Orangeliquid OSRS Bank Evaluator", page_icon="assets/orange_alien.ico")


def main():
    if "db_initialized" not in st.session_state:
        init_db()
        st.session_state.db_initialized = True

    # Header Creation
    st.markdown(
        "<h1 style='color:#FFA500; text-align: center; '>ORANGELIQUID</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h2 style='color:#4227F5; text-align: center; text-style: italic; padding-bottom: 40px;'>"
        "<i>OSRS Bank Evaluator</i></h2>",
        unsafe_allow_html=True
    )

    if "page" not in st.session_state:
        st.session_state.page = "bank_browser"

    bank_browser, compare_item_prices, compare_bank_snapshots = st.columns([1, 1, 1])
    with bank_browser:
        if st.button(label="View Bank Snapshots", type="primary", width="stretch"):
            st.session_state.page = "bank_browser"

    with compare_item_prices:
        if st.button(label="Compare Item Prices", type="primary", width="stretch"):
            st.session_state.page = "compare_item"

    with compare_bank_snapshots:
        if st.button(label="Compare Snapshots", type="primary", width="stretch"):
            st.session_state.page = "compare_bank_snapshots"

    if st.session_state.page == "bank_browser":
        display_bank_browser()
    elif st.session_state.page == "compare_item":
        display_item_compare()
    elif st.session_state.page == "compare_bank_snapshots":
        display_snapshot_compare()


if __name__ == '__main__':
    main()
