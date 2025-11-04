import pandas as pd
import numpy as np
import streamlit as st

from app.crud.database import get_all_banks, get_bank_id_by_name, read_all_items_by_bank_id
from app.database import SessionLocal
from app.utils.transformers import to_dataframe, reorder_df, add_style_to_df
from ui.utils.valuation import calculate_valuation, create_item_valuation_list


def display_snapshot_compare():
    with SessionLocal() as db:
        all_banks = get_all_banks(db=db)

    if not all_banks:
        st.warning("Please select 'Import New Bank' and follow instructions to start")

    elif len(all_banks) < 2:
        st.warning("Only one bank snapshot found, please add another snapshot in 'View Bank Snapshots' for comparison")

    else:
        all_bank_options = [bank.name for bank in all_banks]

        bank_1, bank_2 = st.columns(2)

        # Selection of 2 banks
        with bank_1:
            selected_bank_1 = st.selectbox(label="Select a bank", options=all_bank_options, key="bank_1", index=0)

        with bank_2:
            selected_bank_2 = st.selectbox(label="Select a bank", options=all_bank_options, key="bank_2", index=1)

        st.write("**Data Frame Filters**")

        # Filter selection in two cols
        options_col_1, options_col_2 = st.columns(2)

        with options_col_1:
            options_1 = {
                "is_tradeable": st.checkbox(label="is_tradeable", key="is_tradeable"),
                "uncharged_id": st.checkbox(label="uncharged_id", key="uncharged_id")
            }

        with options_col_2:
            options_2 = {
                "has_ornament_kit_equipped":
                    st.checkbox(label="has_ornament_kit_equipped", key="has_ornament_kit_equipped"),
                "item_id":
                    st.checkbox(label="item_id", key="item_id")
            }

        # Options appended to column_order for use in df creation
        column_order = ["name", "quantity"]

        for key, selected in options_1.items():
            if selected:
                column_order.append(key)

        for key, selected in options_2.items():
            if selected:
                column_order.append(key)

        # DF creation broken into 2 cols
        df_1, df_2 = st.columns(2)

        with df_1:
            with SessionLocal() as db:
                df_1_bank_id = get_bank_id_by_name(db=db, bank_name=selected_bank_1)
                df_1_all_bank_items = read_all_items_by_bank_id(db=db, bank_id=df_1_bank_id)

            df = to_dataframe(entries=df_1_all_bank_items, column_order=column_order)

            # Pandas changed uncharged_id from int to float if not Null -> reverting back to int for UI, id is not float
            if options_1["uncharged_id"]:
                df["uncharged_id"] = df["uncharged_id"].astype("Int64")

            styled_df = add_style_to_df(df=df)

            st.markdown(
                f"<h4 style='text-align: center;'>{selected_bank_1}</h4>",
                unsafe_allow_html=True
            )
            st.dataframe(data=styled_df, hide_index=True)

        with df_2:
            with SessionLocal() as db:
                df_2_bank_id = get_bank_id_by_name(db=db, bank_name=selected_bank_2)
                df_2_all_bank_items = read_all_items_by_bank_id(db=db, bank_id=df_2_bank_id)

            df = to_dataframe(entries=df_2_all_bank_items, column_order=column_order)

            # Pandas changed uncharged_id from int to float if not Null -> reverting back to int for UI, id is not float
            if options_1["uncharged_id"]:
                df["uncharged_id"] = df["uncharged_id"].astype("Int64")

            styled_df = add_style_to_df(df=df)

            st.markdown(
                f"<h4 style='text-align: center;'>{selected_bank_2}</h4>",
                unsafe_allow_html=True
            )
            st.dataframe(data=styled_df, hide_index=True)

        # Gp Valuation expander
        with st.expander(label="GP Valuations"):
            bank_1_val, bank_2_val = st.columns(2)

            with bank_1_val:
                st.write(f"**{selected_bank_1}**")
                total_low_value, total_mean_value, total_high_value = calculate_valuation(
                    all_bank_items=df_1_all_bank_items,
                    db=db,
                    selected_bank=selected_bank_1
                )

                st.write(f"Low: {total_low_value:,}")
                st.write(f"Mean: {int(total_mean_value):,}")
                st.write(f"High: {total_high_value:,}")

            with bank_2_val:
                st.write(f"**{selected_bank_2}**")
                total_low_value, total_mean_value, total_high_value = calculate_valuation(
                    all_bank_items=df_2_all_bank_items,
                    db=db,
                    selected_bank=selected_bank_2
                )

                st.write(f"Low: {total_low_value:,}")
                st.write(f"Mean: {int(total_mean_value):,}")
                st.write(f"High: {total_high_value:,}")

        # Comparisons expander
        with (st.expander(label="Comparisons")):
            bank_1_valuation_data = create_item_valuation_list(
                all_bank_items=df_1_all_bank_items,
                db=db,
                selected_bank=selected_bank_1
            )

            bank_2_valuation_data = create_item_valuation_list(
                all_bank_items=df_2_all_bank_items,
                db=db,
                selected_bank=selected_bank_2
            )

            valuation_options = ["low_value", "mean_value", "high_value"]
            valuation_type_selected = st.selectbox(label="**Valuation Options**", index=1, options=valuation_options)

            column_order = ["name", "quantity", valuation_type_selected]

            df_bank_1 = reorder_df(df=pd.DataFrame(bank_1_valuation_data), order=column_order)
            df_bank_2 = reorder_df(df=pd.DataFrame(bank_2_valuation_data), order=column_order)

            merged_df = pd.merge(
                df_bank_1,
                df_bank_2,
                on="name",
                how="outer",
                suffixes=(f"_{selected_bank_1}", f"_{selected_bank_2}")
            )

            # Create quantity_diff col
            merged_df["quantity_diff"] = (
                (
                    merged_df[f"quantity_{selected_bank_1}"].fillna(0) -
                    merged_df[f"quantity_{selected_bank_2}"].fillna(0)
                )
                .abs()
            )

            # Create valuation diff col depending on valuation_type_selected
            merged_df[f"{valuation_type_selected}_diff"] = (
                (
                    merged_df[f"{valuation_type_selected}_{selected_bank_1}"].fillna(0) -
                    merged_df[f"{valuation_type_selected}_{selected_bank_2}"].fillna(0)
                )
                .abs()
            )

            merged_df["quantity_direction"] = np.select(
                [
                    merged_df[f"quantity_{selected_bank_1}"].isna() & ~merged_df[f"quantity_{selected_bank_2}"].isna(),
                    merged_df[f"quantity_{selected_bank_2}"].isna() & ~merged_df[f"quantity_{selected_bank_1}"].isna(),
                    merged_df[f"quantity_{selected_bank_1}"] > merged_df[f"quantity_{selected_bank_2}"],
                    merged_df[f"quantity_{selected_bank_1}"] < merged_df[f"quantity_{selected_bank_2}"],
                ],
                [
                    f"'{selected_bank_1}' missing",
                    f"'{selected_bank_2}' missing",
                    f"'{selected_bank_1}' higher",
                    f"'{selected_bank_2}' higher",
                ],
                default="No Difference",
            )

            styled_df = add_style_to_df(df=merged_df)

            st.dataframe(data=styled_df, hide_index=True)

            # display top 10 most valuable items in bank
            st.write("**Top 10 Most Highest Value by Mean**")

            st.write(selected_bank_1)
            bank_1_top_10_mean = add_style_to_df(df=df_bank_1.nlargest(10, 'mean_value'))
            st.dataframe(data=bank_1_top_10_mean, hide_index=True)

            st.write(selected_bank_2)
            bank_2_top_10_mean = add_style_to_df(df=df_bank_2.nlargest(10, 'mean_value'))
            st.dataframe(data=bank_2_top_10_mean, hide_index=True)

            # Display top 10 highest quantity items in bank
            st.write("**Top 10 Highest Quantity of Items**")
            st.write(selected_bank_1)
            bank_1_top_10_q = add_style_to_df(df=df_bank_1.nlargest(10, 'quantity'))
            st.dataframe(data=bank_1_top_10_q, hide_index=True)

            st.write(selected_bank_2)
            bank_2_top_10_q = add_style_to_df(df=df_bank_2.nlargest(10, 'quantity'))
            st.dataframe(data=bank_2_top_10_q, hide_index=True)

