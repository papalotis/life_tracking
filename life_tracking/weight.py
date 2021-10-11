from datetime import date
from typing import Sequence

import altair as alt
import pandas as pd
import streamlit as st
from deta import Deta
from pydantic import BaseModel, constr

deta = Deta(st.secrets["deta_project_key"])

base = deta.Base("weight")


class Entry(BaseModel):
    value: float
    date: date
    comment: constr(strip_whitespace=True)


def upload_entry(entry: Entry) -> None:
    base.put(entry.json())
    import streamlit.legacy_caching

    streamlit.legacy_caching.clear_cache()


@st.cache
def load_entries() -> Sequence[Entry]:
    return sorted(
        (Entry.parse_raw(data["value"]) for data in base.fetch().items),
        key=lambda entry: entry.date,
    )


def main() -> None:

    past_entries: Sequence[Entry] = load_entries()

    with st.expander("Show entries", expanded=True):
        dates = [entry.date for entry in past_entries]
        values = [entry.value for entry in past_entries]

        data = pd.DataFrame({"weight": values, "date": dates})

        chart = alt.Chart(data).mark_line().encode(x="date:T", y="weight:Q")

        st.altair_chart(chart)

        st.write(data)

    with st.expander("Add entry"):
        try:
            last_value = past_entries[-1].value
        except IndexError:
            last_value = 0.0

        entry_weight_in_kg = st.number_input(
            "Weight in kg",
            min_value=0.0,
            step=0.1,
            value=last_value,
            format="%.1f",
        )
        entry_date = st.date_input("Date")
        entry_comment = st.text_input("Comment")
        new_entry = Entry(
            value=entry_weight_in_kg, date=entry_date, comment=entry_comment
        )

        st.button("Upload Entry", on_click=upload_entry, kwargs=dict(entry=new_entry))
