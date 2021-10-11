from datetime import datetime
from typing import Sequence

import pandas as pd
import plotly.express as px
import streamlit as st
from deta import Deta, _Base
from pydantic import parse_obj_as

from .entry import Entry, EntryType

st.set_page_config(page_title="Tracking")

deta = Deta(st.secrets["deta_project_key"])


def upload_entry(base: _Base, entry: Entry) -> None:
    import json

    base.put(json.loads(entry.json()))
    import streamlit.legacy_caching

    streamlit.legacy_caching.clear_cache()


@st.cache(hash_funcs={_Base: lambda base: base.base_path})
def load_db(base: _Base) -> Sequence[Entry]:
    return parse_obj_as(Sequence[Entry], base.fetch().items)


def main() -> None:

    mode: EntryType = st.radio(
        "Mode", list(EntryType), format_func=lambda mode: mode.value.capitalize()
    )

    with st.expander("New entry"):

        base = deta.Base(mode.value)

        column1, column2 = st.columns([1, 1])

        value = st.number_input("Value")
        with column1:
            date = st.date_input("Date")
        with column2:
            time = st.time_input("Time")
        comment = st.text_input("Comments")

        datetime_object = datetime.combine(date, time)

        entry = Entry(
            value=value, datetime=datetime_object, comment=comment, type=mode.value
        )

        st.button("Upload entry", on_click=upload_entry, args=(base, entry))

    data = load_db(base)
    data_df = pd.DataFrame([entry.dict() for entry in data])[
        ["value", "datetime", "comment"]
    ]
    data_df["date"] = data_df["datetime"].dt.date

    plot_type = px.line if mode == EntryType.weight else px.bar

    fig = plot_type(data_df, x="date", y="value", text="comment")
    fig.update_xaxes(rangeslider_visible=True)

    st.plotly_chart(fig)

    st.write(data_df)
