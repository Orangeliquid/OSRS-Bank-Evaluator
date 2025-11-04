import pandas as pd
import streamlit as st

from app.crud.database import get_all_banks, read_item_quantity_by_bank_item_id
from app.database import SessionLocal
from app.crud.database import read_single_item_snapshots, get_similar_item_snapshots
from app.utils.transformers import to_dataframe, reorder_df, add_style_to_df
from app.utils.snapshot import enter_all_items_current_price


def display_item_compare():
    with SessionLocal() as db:
        all_banks = get_all_banks(db=db)

    if not all_banks:
        st.warning("Please import a bank snapshot by clicking 'View Bank Snapshots' button")
    else:
        all_bank_options = [bank.name for bank in all_banks]
        selected_bank = st.selectbox(label="Select a bank", options=all_bank_options)

        if st.button(label="Get Current Prices"):
            can_create_snapshot, remaining_cooldown = enter_all_items_current_price(bank_name=selected_bank)
            if can_create_snapshot:
                st.success("New prices fetched - new snapshots created")
            else:
                st.warning(
                    f"Only one snapshot may be entered a day. "
                    f"Remaining cooldown: {remaining_cooldown}"
                )

        requested_item = st.text_input(label="Search an item")

        if not requested_item:
            st.info("Enter an item name to search.")
            return

        with SessionLocal() as db:
            item_snapshots = read_single_item_snapshots(
                db=db,
                item_name=requested_item.capitalize(),
                bank_name=selected_bank,
            )

            if item_snapshots:
                df = to_dataframe(entries=item_snapshots)

                item_quantity = read_item_quantity_by_bank_item_id(db=db, bank_item_id=item_snapshots[0].bank_item_id)

                # add quantity and single_item_price to df
                df["quantity"] = item_quantity
                df["single_item_price"] = df["mean_value_estimate"] / item_quantity

                # add commas to numbers for readability
                for col in ["low_value_estimate", "mean_value_estimate", "high_value_estimate", "single_item_price"]:
                    df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)

                column_order = [
                    "item_name",
                    "quantity",
                    "single_item_price",
                    "low_value_estimate",
                    "mean_value_estimate",
                    "high_value_estimate",
                    "timestamp",
                ]

                df = reorder_df(df=df, order=column_order)

                styled_df = add_style_to_df(df=df)

                st.markdown(f"<h4 style='text-align: center;'>{requested_item.capitalize()}</h4>", unsafe_allow_html=True)

                st.dataframe(data=styled_df, hide_index=True)

                return

            similar_items = get_similar_item_snapshots(
                db=db,
                user_entry=requested_item.capitalize(),
                bank_name=selected_bank,
            )

            if not similar_items:
                st.error(f"No similar items detected in database for '{requested_item}'.")
            else:
                st.warning(f"No exact match found for '{requested_item}'. Did you mean?: ")
                for item in similar_items:
                    with st.expander(f"- **{item.name}**"):
                        snapshots = read_single_item_snapshots(
                            db=db,
                            item_name=item.name,
                            bank_name=selected_bank,
                        )
                        if snapshots:
                            df = to_dataframe(entries=snapshots)

                            item_quantity = read_item_quantity_by_bank_item_id(
                                db=db,
                                bank_item_id=snapshots[0].bank_item_id,
                            )

                            # add quantity and single_item_price to df
                            df["quantity"] = item_quantity
                            df["single_item_price"] = df["mean_value_estimate"] / item_quantity

                            # add commas to numbers for readability
                            for col in ["low_value_estimate", "mean_value_estimate", "high_value_estimate", "single_item_price"]:
                                df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)

                            column_order = [
                                "item_name",
                                "quantity",
                                "single_item_price",
                                "low_value_estimate",
                                "mean_value_estimate",
                                "high_value_estimate",
                                "timestamp",
                            ]

                            df = reorder_df(df=df, order=column_order)

                            styled_df = add_style_to_df(df=df)

                            st.dataframe(data=styled_df, hide_index=True)
                        else:
                            st.write(f"{item.name} is untradeable!")
