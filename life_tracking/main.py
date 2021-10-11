from datetime import datetime

import streamlit as st
from deta import Deta, _Base

from .entry import Entry, EntryType

st.set_page_config(page_title="Tracking")

deta = Deta(st.secrets["deta_project_key"])


def upload_entry(base: _Base, entry: Entry) -> None:
    import json

    base.put(json.loads(entry.json()))
    import streamlit.legacy_caching

    streamlit.legacy_caching.clear_cache()


def main() -> None:

    mode: EntryType = st.radio(
        "Mode", EntryType, format_func=lambda mode: mode.value.capitalize()
    )

    base = deta.Base(mode.value)

    column1, column2 = st.columns([1, 1])

    value = st.number_input("Value")
    with column1:
        date = st.date_input("Date")
    with column2:
        time = st.time_input("Time")
    comment = st.text_input("Comments")

    datetime_object = datetime.combine(date, time)

    st.write(mode)

    entry = Entry(
        value=value, datetime=datetime_object, comment=comment, type=mode.value
    )

    st.button("Upload entry", on_click=upload_entry, args=(base, entry))
