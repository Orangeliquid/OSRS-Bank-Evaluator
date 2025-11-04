import streamlit as st

from app.database import SessionLocal
from app.crud.database import get_all_banks, get_bank_id_by_name, read_all_items_by_bank_id, delete_bank
from app.crud.database import read_latest_item_snapshot, bank_name_is_unique
from app.utils.transformers import to_dataframe, add_style_to_df
from app.utils.file_io import enter_tsv_into_db, convert_all_items_to_json
from app.utils.snapshot import initial_enter_all_items_current_price
from ui.utils.clipboard import verify_tsv
from app.utils.file_io import delete_file
from ui.utils.valuation import calculate_valuation


def display_bank_browser():
    with SessionLocal() as db:
        all_banks = get_all_banks(db=db)

    if not all_banks:
        st.warning("Please select 'Import New Bank' and follow instructions to start")

    with st.expander(label="Import New Bank"):
        st.info("1. Log into Runelight")
        st.info("2. Go to bank in OSRS and open your bank")
        st.info("3. Verify Runelite plugin 'Bank Memory' is installed")
        st.info("4. Click 'Bank Memory' icon on the right to pull up the panel to see plugin")
        st.info("5. Click the 'Saved Banks' Tab at the top of the plugin panel")
        st.info("6. Right click 'Current Bank' and click 'Save Snapshot'")
        st.info("7. Choose a name for bank snapshot and press 'OK'")
        st.info("8. The saved snapshots let you re-enter them into the db if deleted on accident")
        st.info("9. Right click the new saved snapshot and click 'Copy item data to clipboard'")
        st.info("10. Enter your desired name for this bank below(Example: Original Bank)")

        bank_name_input = st.text_input("Bank Name")

        # Initialize session state flags
        if "bank_submitted" not in st.session_state:
            st.session_state.bank_submitted = False

        if st.button(label="Submit Bank Data", type="primary"):
            if not bank_name_input:
                st.error("Please enter a bank name for this snapshot")

            else:
                with SessionLocal() as db:
                    is_name_unique = bank_name_is_unique(db=db, bank_name=bank_name_input)

                if not is_name_unique:
                    st.error(f"{bank_name_input} already exist. Delete existing Bank or choose new name")
                else:
                    is_tsv, bank_data = verify_tsv()
                    if is_tsv:
                        enter_tsv_into_db(tsv_data=bank_data, file_name=bank_name_input)
                        total_bank_items = convert_all_items_to_json(file_name=bank_name_input)
                        st.session_state.bank_submitted = True
                        st.session_state.bank_name_input = bank_name_input
                        st.session_state.total_bank_items = total_bank_items
                        st.success(f"Bank data loaded. Total items: {total_bank_items}")
                    else:
                        st.error("Clipboard contents are not valid TSV data.")

        if st.session_state.bank_submitted:
            bank_name_input = st.session_state.bank_name_input
            st.warning(f"Is this the correct number of items in '{bank_name_input}'? ({st.session_state.total_bank_items})")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Bank item count is CORRECT"):
                    with SessionLocal() as db:
                        initial_enter_all_items_current_price(
                            db=db,
                            file_name=bank_name_input,
                            bank_name=bank_name_input
                        )

                    # Clean up temp files and rerun
                    for file_type in ["txt", "json"]:
                        delete_file(file_name=bank_name_input, file_type=file_type)

                    st.session_state.bank_submitted = False
                    st.rerun()

            with col2:
                if st.button("INCORRECT bank item count"):
                    st.error("Bank not added to database")
                    for file_type in ["txt", "json"]:
                        delete_file(file_name=bank_name_input, file_type=file_type)

                    st.session_state.bank_submitted = False
                    st.rerun()

    if all_banks:
        all_bank_options = [bank.name for bank in all_banks]
        # Logic for bank snapshot deletion
        with st.expander(label="Delete Bank Snapshot"):
            st.warning("Warning! This will delete everything in the database entered related to your selected bank.")
            bank_to_delete = st.selectbox(label="Select Bank to Delete", options=all_bank_options)
            if st.button(f"Submit deletion of '{bank_to_delete}'"):
                with SessionLocal() as db:
                    deletion_status = delete_bank(db=db, bank_name=bank_to_delete)

                if deletion_status:
                    st.success(f"Successfully deleted: {bank_to_delete}")
                    st.rerun()
                else:
                    st.warning(f"Failed to delete: {bank_to_delete}, may not exist.")
                    st.rerun()

        # Logic for DF creation
        selected_bank = st.selectbox(label="Select a bank", options=all_bank_options)

        with SessionLocal() as db:
            bank_id = get_bank_id_by_name(db=db, bank_name=selected_bank)
            all_bank_items = read_all_items_by_bank_id(db=db, bank_id=bank_id)

        column_order = [
            "name", "quantity", "is_tradeable", "uncharged_id", "has_ornament_kit_equipped", "item_id"
        ]
        df = to_dataframe(entries=all_bank_items, column_order=column_order)

        # Pandas changed uncharged_id from int to float if not Null -> reverting back to int for UI, id is not float
        df["uncharged_id"] = df["uncharged_id"].astype("Int64")

        styled_df = add_style_to_df(df=df)

        if st.checkbox(label="Show All Bank Items", value=False, width="content"):
            st.markdown(
                f"<h4 style='text-align: center;'>Items In '{selected_bank}'</h4>",
                unsafe_allow_html=True
            )
            st.dataframe(data=styled_df, hide_index=True)

            total_low_value, total_mean_value, total_high_value = calculate_valuation(
                all_bank_items=all_bank_items,
                db=db,
                selected_bank=selected_bank
            )

            st.write("**GP Valuation**")

            left, mid, right = st.columns(3)

            with left:
                st.write(f"Low: {total_low_value:,}")

            with mid:
                st.write(f"Mean: {int(total_mean_value):,}")

            with right:
                st.write(f"High: {total_high_value:,}")
