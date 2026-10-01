import altair as alt
import pandas as pd
import streamlit as st

from connect_data_warehouse import query_job_listings

st.set_page_config(
    page_title="Technical field job ads",
    page_icon="🛠️",
    layout="wide",
)

ACCENT = "#3B82C4"

# Columns that may or may not exist in mart_technical_jobs.
# The dashboard uses the first match it finds and skips a section if none exists.
OPTIONAL_COLUMNS = {
    "employer": ["employer_name", "employer_workplace", "employer"],
    "city": ["workplace_city", "workplace_municipality", "city", "municipality"],
    "region": ["workplace_region", "region"],
    "headline": ["headline", "title"],
    "deadline": ["application_deadline", "deadline"],
    "employment_type": ["employment_type"],
    "duration": ["duration"],
}


# ---------- data ----------


@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    df = query_job_listings()
    df.columns = df.columns.str.lower()
    return df


def find_column(df: pd.DataFrame, key: str):
    for candidate in OPTIONAL_COLUMNS[key]:
        if candidate in df.columns:
            return candidate
    return None


def top_n(df: pd.DataFrame, column: str, n: int = 10) -> pd.DataFrame:
    return df.groupby(column, dropna=True)["vacancies"].sum().nlargest(n).reset_index()


def bar_chart(data: pd.DataFrame, category: str, title: str):
    chart = (
        alt.Chart(data)
        .mark_bar(color=ACCENT, cornerRadiusEnd=3)
        .encode(
            x=alt.X("vacancies:Q", title="Vacancies"),
            y=alt.Y(
                f"{category}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)
            ),
            tooltip=[
                alt.Tooltip(f"{category}:N", title=title),
                alt.Tooltip("vacancies:Q", title="Vacancies"),
            ],
        )
        .properties(height=max(200, 32 * len(data)))
    )
    st.altair_chart(chart, use_container_width=True)


# ---------- layout ----------


def sidebar_filters(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    st.sidebar.header("Filter")

    groups = sorted(df["occupation_group"].dropna().unique())
    chosen_groups = st.sidebar.multiselect("Occupation group", groups)
    if chosen_groups:
        df = df[df["occupation_group"].isin(chosen_groups)]

    place_col = cols["region"] or cols["city"]
    if place_col:
        places = sorted(df[place_col].dropna().unique())
        label = "Region" if place_col == cols["region"] else "City"
        chosen_places = st.sidebar.multiselect(label, places)
        if chosen_places:
            df = df[df[place_col].isin(chosen_places)]

    search = st.sidebar.text_input("Search occupation or headline")
    if search:
        text_cols = ["occupation"] + ([cols["headline"]] if cols["headline"] else [])
        mask = pd.Series(False, index=df.index)
        for c in text_cols:
            mask |= df[c].astype(str).str.contains(search, case=False, na=False)
        df = df[mask]

    return df


def kpis(df: pd.DataFrame, cols: dict):
    metrics = [
        ("Vacancies", int(df["vacancies"].sum())),
        ("Job ads", len(df)),
        ("Occupations", df["occupation"].nunique()),
    ]
    if cols["employer"]:
        metrics.append(("Employers", df[cols["employer"]].nunique()))

    for col, (label, value) in zip(st.columns(len(metrics)), metrics):
        col.metric(label, f"{value:,}".replace(",", " "))


def layout():
    try:
        raw = load_data()
    except Exception as err:
        st.error(
            "Could not load data from Snowflake. Check the credentials in "
            f".env and that the reporter role can read the marts.\n\n{err}"
        )
        st.stop()

    cols = {key: find_column(raw, key) for key in OPTIONAL_COLUMNS}

    st.title("Technical field job ads")
    st.caption(
        "Job ads in the technical field from Arbetsförmedlingen's API, "
        "loaded with dlt, modelled with dbt and served from Snowflake."
    )

    df = sidebar_filters(raw, cols)

    if df.empty:
        st.info(
            "No job ads match these filters. Clear a filter in the sidebar to see results."
        )
        return

    kpis(df, cols)

    tab_names = ["Occupations"]
    if cols["employer"] or cols["city"] or cols["region"]:
        tab_names.append("Employers and places")
    tab_names.append("Job ads")
    tabs = dict(zip(tab_names, st.tabs(tab_names)))

    with tabs["Occupations"]:
        left, right = st.columns(2)
        with left:
            st.subheader("Top occupation groups")
            bar_chart(
                top_n(df, "occupation_group"), "occupation_group", "Occupation group"
            )
        with right:
            st.subheader("Top occupations")
            bar_chart(top_n(df, "occupation"), "occupation", "Occupation")

    if "Employers and places" in tabs:
        with tabs["Employers and places"]:
            left, right = st.columns(2)
            if cols["employer"]:
                with left:
                    st.subheader("Employers with most vacancies")
                    bar_chart(top_n(df, cols["employer"]), cols["employer"], "Employer")
            place_col = cols["city"] or cols["region"]
            if place_col:
                with right:
                    st.subheader("Where the jobs are")
                    bar_chart(top_n(df, place_col), place_col, "Place")

    with tabs["Job ads"]:
        preferred = [
            cols["headline"],
            "occupation",
            "occupation_group",
            cols["employer"],
            cols["city"] or cols["region"],
            cols["employment_type"],
            cols["duration"],
            cols["deadline"],
            "vacancies",
        ]
        shown = [c for c in dict.fromkeys(preferred) if c and c in df.columns]
        rest = [c for c in df.columns if c not in shown]

        show_all = st.toggle("Show all columns", value=False)
        table = df[shown + rest] if show_all else df[shown]

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config={
                c: st.column_config.Column(c.replace("_", " ").capitalize())
                for c in table.columns
                if c != "vacancies"
            }
            | {"vacancies": st.column_config.NumberColumn("Vacancies", format="%d")},
        )

        st.download_button(
            "Download filtered ads as CSV",
            table.to_csv(index=False).encode("utf-8"),
            file_name="technical_job_ads.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    layout()
