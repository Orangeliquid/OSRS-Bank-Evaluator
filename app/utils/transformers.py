import pandas as pd


def to_dataframe(entries, column_order: list = None):
    data = [entry.__dict__ for entry in entries]

    for d in data:
        d.pop("_sa_instance_state", None)

    df = pd.DataFrame(data)

    if column_order:
        df = reorder_df(df=df, order=column_order)

    return df


def reorder_df(df, order: list):
    return df.reindex(columns=order)


def convert_numeric_like_cols(df):
    # Convert only numeric-like columns to numbers
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df, numeric_cols


def add_style_to_df(df):
    df, numeric_cols = convert_numeric_like_cols(df)
    return (
        df.style
        .set_properties(**{
            "background-color": "#4227F5",
            "color": "#FFFFFF",
        })
        .format({col: "{:,.0f}" for col in numeric_cols})
    )
