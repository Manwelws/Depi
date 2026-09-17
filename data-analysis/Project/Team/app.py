import os
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Ford GoBike — Trip Analytics",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#36A28B", "#911F27", "#5A4FCF"]
GENDER_ORDER = ["Male", "Female", "Other", "Unknown"]

AGE_GROUP_BINS = {"Young": (18, 29), "Adult": (30, 54), "Senior": (55, 120)}
TRIP_YEAR = 2019  # dataset period (Ford GoBike, February 2019); used only when
# timestamps carry no usable date AND the birth-year is present.

DEFAULT_FILE = Path(__file__).resolve().parent / "data" / "processed" / "preprocessed_fordgobike.csv"


# ------------------------------------------------------------------------------
# Data loading & preparation
# ------------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def resolve_data_path() -> str:
    """Dataset path. Env var override wins, otherwise the team preprocessed file."""
    if env := os.environ.get("GOBIKE_DATA_CSV"):
        p = Path(env)
        if p.exists():
            return str(p)
        st.sidebar.warning(f"GOBIKE_DATA_CSV not found: {env}")
    if not DEFAULT_FILE.exists():
        st.sidebar.error(
            f"Dataset not found at:\n\n`{DEFAULT_FILE}`\n\n"
            "Place `preprocessed_fordgobike.csv` in `data/processed/`\n\n"
            "(or set the `GOBIKE_DATA_CSV` environment variable)."
        )
    return str(DEFAULT_FILE)


def _parse_date_ratio(series: pd.Series) -> float:
    """Fraction of rows whose value contains a real date component (ISO or US)."""
    s = series.astype("string").fillna("")
    ok = s.str.match(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}")
    return float(ok.mean()) if len(s) else 0.0


@st.cache_data(ttl=3600, show_spinner=False)
def prepare_df(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Normalise schema, reconstruct engineered features, report time usability."""
    df = df.copy()
    notes = []

    # Duration in minutes -----------------------------------------------------
    if "duration_min" not in df and "duration_sec" in df:
        df["duration_min"] = pd.to_numeric(df["duration_sec"], errors="coerce") / 60.0
        notes.append("duration_min computed from duration_sec.")

    # Gender (reconstructed from one-hot columns when needed) ------------------
    if "member_gender" not in df:
        onehots = {k: f"gender_{k}" for k in GENDER_ORDER}
        if all(c in df.columns for c in onehots.values()):
            df["member_gender"] = np.select(
                [df[c] == 1 for c in onehots.values()],
                list(onehots),
                default="Unknown",
            )
            notes.append("member_gender reconstructed from one-hot columns.")
        else:
            df["member_gender"] = np.nan

    df.loc[df["member_gender"].isna(), "member_gender"] = "Unknown"

    # Age ---------------------------------------------------------------------
    if "age" not in df and "member_birth_year" in df:
        birth = pd.to_numeric(df["member_birth_year"], errors="coerce")
        df["age"] = TRIP_YEAR - birth
        df.loc[(df["age"] < 10) | (df["age"] > 100), "age"] = np.nan
        notes.append(f"age computed as {TRIP_YEAR} − member_birth_year.")

    # Age group ---------------------------------------------------------------
    if df["age"].notna().any():
        if "age_group" not in df:
            age_groups = ["Young", "Adult", "Senior"]
            onehot_cols = [f"age_group_{g}" for g in age_groups]
            if all(c in df.columns for c in onehot_cols):
                df["age_group"] = np.select(
                    [df[c] == 1 for c in onehot_cols],
                    age_groups,
                    default="Unknown",
                )
                notes.append("age_group reconstructed from one-hot columns.")
            else:
                bins = [AGE_GROUP_BINS[g][0] for g in age_groups] + [np.inf]
                labels = age_groups
                df["age_group"] = pd.cut(
                    df["age"], bins=bins, labels=labels, right=True
                ).astype(str)
                df.loc[df["age"].isna(), "age_group"] = "Unknown"
                notes.append("age_group derived from age (18–29 Young, 30–54 Adult, 55+ Senior).")
    else:
        df["age_group"] = "Unknown"

    # Time-feature capability ---------------------------------------------------
    time_info = {"usable_dates": False, "ratio": 0.0}
    if "start_time" in df.columns:
        ratio = _parse_date_ratio(df["start_time"])
        time_info = {"usable_dates": ratio >= 0.5, "ratio": ratio}
        if time_info["usable_dates"]:
            st_ = pd.to_datetime(df["start_time"], errors="coerce")
            df["hour"] = st_.dt.hour
            df["day_of_week"] = st_.dt.day_name()
            df["date"] = st_.dt.date
            df["month"] = st_.dt.to_period("M").astype(str)
            df["trip_year"] = st_.dt.year
            note = "Real timestamps detected — weekday/hour/month features enabled."
            notes.append(note)
        else:
            sample = (
                df["start_time"].astype(str).value_counts().head(6)
                .rename_axis("value")
                .reset_index(name="count")
            )
            time_info["sample"] = sample

    # Round-trip flag -----------------------------------------------------------
    if {"start_station_id", "end_station_id"}.issubset(df.columns):
        df["same_station_trip"] = df["start_station_id"] == df["end_station_id"]

    return df, {"notes": notes, "time": time_info}


# ------------------------------------------------------------------------------
# Plot helpers
# ------------------------------------------------------------------------------
PLOTLY_TEMPLATE = dict(
    layout=dict(
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13, color="#1f2937"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=58, b=10),
        title=dict(x=0.02, xanchor="left", font=dict(size=16, color="#111827")),
        colorway=PALETTE,
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
)


def theme(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    fig.update_layout(template=PLOTLY_TEMPLATE)
    if height:
        fig.update_layout(height=height)
    return fig


def show(fig: go.Figure, *, height: int | None = None):
    st.plotly_chart(theme(fig, height=height), width="stretch")


def count_frame(series: pd.Series, name: str, *, order: list | None = None) -> pd.DataFrame:
    """value_counts() as a clean two-column frame: [name, count]. Optionally reorder rows."""
    out = series.value_counts().rename_axis(name).reset_index(name="count")
    if order:
        out = out.set_index(name).reindex(order).rename_axis(name).reset_index()
    return out


# ------------------------------------------------------------------------------
# Load & prepare
# ------------------------------------------------------------------------------
data_path = resolve_data_path()

try:
    raw_df = load_csv(data_path)
except Exception as exc:  # pragma: no cover - defensive only
    st.error(f"Could not read the dataset file:\n\n{exc}")
    st.stop()

if raw_df.empty:
    st.error("The dataset file contains no rows.")
    st.stop()

prepared, meta = prepare_df(raw_df)

# ------------------------------------------------------------------------------
# Sidebar — data source & filters
# ------------------------------------------------------------------------------
st.sidebar.title("🚲 Dashboard Controls")
st.sidebar.caption(f"File:\n`{Path(data_path).name}`")
st.sidebar.success(f"{len(raw_df):,} rows · {raw_df.shape[1]} columns")

with st.sidebar.expander("ℹ️ Data preparation"):
    st.caption("\n".join(f"• {n}" for n in meta["notes"]))
    t = meta["time"]
    if not t["usable_dates"]:
        st.caption(
            "**Time warning:** `start_time`/`end_time` hold time-of-day strings with no "
            "date component (e.g. `32:10.1`). Day-of-week / hour / month trends and the "
            "date filter are therefore disabled."
        )

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

df = prepared.copy()

# Date range ----------------------------------------------------------------
if meta["time"]["usable_dates"] and "date" in df.columns:
    min_date, max_date = df["date"].min(), df["date"].max()
    if isinstance(min_date, pd.Timestamp):
        min_date, max_date = min_date.date(), max_date.date()
    chosen = st.sidebar.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(chosen, tuple) and len(chosen) == 2:
        d0, d1 = chosen
        df = df[(df["date"] >= d0) & (df["date"] <= d1)]
else:
    st.sidebar.caption("Date filter disabled (no valid dates in data).")


def apply_multiselect(df: pd.DataFrame, label: str, col: str, *, order: list | None = None) -> pd.DataFrame:
    """Filter df through a sidebar multiselect; returns the filtered copy."""
    if col not in df.columns or df[col].dropna().empty:
        return df
    options = sorted(df[col].dropna().unique().tolist())
    if order:
        options = [o for o in order if o in options]
    if not options:
        return df
    selected = st.sidebar.multiselect(label, options, default=options)
    return df[df[col].isin(selected)]


df = apply_multiselect(df, "User type", "user_type")
df = apply_multiselect(df, "Gender", "member_gender")
df = apply_multiselect(
    df, "Age group", "age_group", order=["Young", "Adult", "Senior", "Unknown"]
)

# Duration slider -------------------------------------------------------------
if "duration_min" in df.columns and df["duration_min"].notna().any():
    lo = float(np.floor(df["duration_min"].min()))
    hi = float(np.ceil(df["duration_min"].quantile(0.999)))
    default_hi = float(np.ceil(df["duration_min"].quantile(0.99)))
    if hi > lo:
        rng = st.sidebar.slider(
            "Trip duration (minutes)",
            lo, hi, (lo, min(default_hi, hi)),
            help="Default view hides the longest 1% of rides; drag to include them.",
        )
        df = df[(df["duration_min"] >= rng[0]) & (df["duration_min"] <= rng[1])]

if "same_station_trip" in df.columns:
    if st.sidebar.checkbox("Round trips only (same start & end station)"):
        df = df[df["same_station_trip"]]

st.sidebar.markdown("---")
st.sidebar.caption(f"Rows after filtering: **{len(df):,}**")

# ------------------------------------------------------------------------------
# Header & KPIs
# ------------------------------------------------------------------------------
st.markdown(
    """
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:2px;">
      <span style="font-size:38px;">🚲</span>
      <div>
        <div style="font-size:26px;font-weight:700;color:#111827;">Ford GoBike — Trip Analytics</div>
        <div style="color:#6b7280;font-size:14px;">Interactive dashboard · February 2019 ride share · preprocessed trip data</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

if len(df) == 0:
    st.warning("No trips match the current filters. Widen your selection to continue.")
    st.stop()

n = len(df)
sub_pct = 100 * df["user_type"].eq("Subscriber").mean() if "user_type" in df.columns else np.nan

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Trips", f"{n:,}", help="Trips matching the current filters.")
k2.metric("Avg Duration", f"{df['duration_min'].mean():.1f} min", help="Arithmetic mean trip duration.")
k3.metric("Median Duration", f"{df['duration_min'].median():.1f} min", help="Middle value of trip duration.")
k4.metric("Unique Bikes", f"{df['bike_id'].nunique():,}", help="Distinct bikes in service.")
k5.metric("Subscriber %", f"{sub_pct:.1f}%", help="Share of trips by Subscribers vs Customers.")
if {"member_birth_year", "member_gender"}.issubset(df.columns):
    est = df.dropna(subset=["member_birth_year"]).groupby(
        ["member_birth_year", "member_gender"], dropna=False
    ).ngroups
    k6.metric("Distinct Riders (est.)", f"{est:,}",
              help="Distinct birth-year × gender profiles — an estimate, no member ID is available.")

# ------------------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------------------
tab_overview, tab_time, tab_stations, tab_riders, tab_quality, tab_data = st.tabs(
    ["📊 Overview", "🕒 Time Analysis", "📍 Stations & Map", "🧑 Rider Demographics", "🔍 Data Quality", "🗂️ Raw Data"]
)

# ---- Overview -----------------------------------------------------------------
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        hist_df = df[df["duration_min"] < df["duration_min"].quantile(0.98)]
        fig = px.histogram(
            hist_df, x="duration_min", nbins=40,
            title="Trip Duration Distribution",
            labels={"duration_min": "Duration (minutes)"},
            color_discrete_sequence=["#2E86AB"],
        )
        fig.update_layout(xaxis_range=[0, 60], bargap=0.05)
        show(fig, height=340)
        st.caption("Right-skewed: most rides are short; the axis is clipped at 60 min "
                   "for readability (long rides still counted). Median ≈ "
                   f"{df['duration_min'].median():.1f} min.")

    with c2:
        counts = count_frame(df["user_type"], "user_type")
        fig = px.bar(
            counts, x="user_type", y="count", color="user_type",
            title="Subscriber vs Customer",
            labels={"count": "Trips", "user_type": "User type"},
            color_discrete_sequence=["#2E86AB", "#F18F01"],
        )
        fig.update_layout(showlegend=False, bargap=0.35)
        show(fig, height=340)
        dur_by_user = df.groupby("user_type")["duration_min"].mean()
        if len(dur_by_user) >= 2:
            longest, shortest = dur_by_user.idxmax(), dur_by_user.idxmin()
            st.caption(
                f"Subscribers dominate the service. {longest} take fewer trips but "
                f"ride ~{dur_by_user[longest] / dur_by_user[shortest]:.1f}× longer "
                f"on average ({dur_by_user[longest]:.1f} vs {dur_by_user[shortest]:.1f} min)."
            )

    c3, c4 = st.columns(2)
    with c3:
        if "bike_share_for_all_trip" in df.columns:
            counts = count_frame(df["bike_share_for_all_trip"], "program")
            fig = px.bar(
                counts, x="program", y="count", color="program",
                title="Bike Share For All Trips",
                color_discrete_sequence=["#A23B72", "#36A28B"],
            )
            fig.update_layout(showlegend=False, bargap=0.35)
            show(fig, height=340)
            st.caption("Most trips are not part of the Bike Share for All program.")

    with c4:
        if "same_station_trip" in df.columns:
            counts = count_frame(
                df["same_station_trip"].map({True: "Round trip", False: "One-way"}),
                "trip_type",
            )
            fig = px.pie(
                counts, names="trip_type", values="count", hole=0.45,
                title="Round Trip vs One-Way", color_discrete_sequence=["#A23B72", "#F18F01"],
            )
            show(fig, height=340)
            st.caption("The vast majority of trips end at a different station than they start.")

# ---- Time Analysis -------------------------------------------------------------
with tab_time:
    if meta["time"]["usable_dates"]:
        daily = df.groupby("date").size().reset_index(name="trips")
        fig = px.line(daily, x="date", y="trips", title="Trips Over Time", markers=True)
        show(fig, height=320)

        c1, c2 = st.columns(2)
        with c1:
            hourly = df.groupby("hour").size().reindex(range(24), fill_value=0).rename("trips").reset_index()
            fig = px.bar(hourly, x="hour", y="trips", title="Trips by Hour of Day",
                         color_discrete_sequence=["#2E86AB"])
            fig.update_layout(xaxis=dict(dtick=1))
            show(fig, height=330)
        with c2:
            dow = df["day_of_week"].value_counts().reindex(DOW_ORDER).rename("trips").reset_index()
            fig = px.bar(dow, x="day_of_week", y="trips", title="Trips by Day of Week",
                         color_discrete_sequence=["#A23B72"])
            show(fig, height=330)

        heat = df.groupby(["day_of_week", "hour"]).size().reset_index(name="trips")
        heat_pivot = heat.pivot(index="day_of_week", columns="hour", values="trips").reindex(DOW_ORDER)
        fig = px.imshow(
            heat_pivot, aspect="auto", color_continuous_scale="Blues",
            title="Trip Volume Heatmap (Day of Week × Hour)",
            labels=dict(x="Hour", y="Day of Week", color="Trips"),
        )
        show(fig, height=340)
    else:
        st.warning("## ⚠️ Time-based analysis is unavailable for this dataset")
        st.markdown(
            "The `start_time` / `end_time` columns of the raw and preprocessed files contain "
            "**time-of-day strings with no date component** — for example `32:10.1`, `54:26.0`."
            " These values are not valid timestamps, so day-of-week, hour-of-day and month "
            "trends **cannot be computed without fabricating data**."
        )
        m1, m2, m3 = st.columns(3)
        m2.metric("Rows with a real date", f"{int(meta['time']['ratio'] * len(df)):,}",
                  help="Rows whose start_time contains a parseable date component.")
        m1.metric("Rows analysed", f"{len(df):,}")
        m3.metric("Date coverage", f"{meta['time']['ratio']:.1%}")

        st.markdown("### What the raw values look like")
        sample = meta["time"].get("sample", pd.DataFrame())
        if not sample.empty:
            st.dataframe(sample, width="stretch", height=220, hide_index=True)
        st.info(
            "**Next step:** re-run preprocessing from the original timestamps (e.g. "
            "`2019-02-06 07:23:54`) so the date is kept. This dashboard **auto-enables** "
            "the weekday / hour / month panels as soon as the file contains real dates."
        )

# ---- Stations & Map -------------------------------------------------------------
with tab_stations:
    c1, c2 = st.columns(2)
    with c1:
        top_start = df["start_station_name"].value_counts().head(10).rename_axis("station").reset_index(name="trips")
        fig = px.bar(top_start.sort_values("trips"), x="trips", y="station", orientation="h",
                     title="Top 10 Start Stations", color_discrete_sequence=["#2E86AB"])
        fig.update_layout(yaxis=dict(tickfont=dict(size=11)))
        show(fig, height=400)
    with c2:
        top_end = df["end_station_name"].value_counts().head(10).rename_axis("station").reset_index(name="trips")
        fig = px.bar(top_end.sort_values("trips"), x="trips", y="station", orientation="h",
                     title="Top 10 End Stations", color_discrete_sequence=["#A23B72"])
        fig.update_layout(yaxis=dict(tickfont=dict(size=11)))
        show(fig, height=400)

    st.subheader("Top station-to-station flows")
    flows = (
        df.groupby(["start_station_name", "end_station_name"]).size()
        .rename("trips").reset_index().sort_values("trips", ascending=False).head(15)
    )
    flows["flow"] = flows["start_station_name"] + "  →  " + flows["end_station_name"]
    fig = px.bar(flows.sort_values("trips"), x="trips", y="flow", orientation="h",
                 color="trips", color_continuous_scale="Viridis",
                 labels={"flow": "Route (start → end)"})
    fig.update_layout(yaxis=dict(tickfont=dict(size=10)))
    show(fig, height=460)

    if {"start_station_latitude", "start_station_longitude", "start_station_name"}.issubset(df.columns):
        st.subheader("Station activity map")
        try:
            station_agg = (
                df.groupby(["start_station_name", "start_station_latitude", "start_station_longitude"])
                .size().rename("trips").reset_index()
            )
            station_agg = station_agg.dropna(
                subset=["start_station_latitude", "start_station_longitude"]
            )
            if station_agg.empty:
                st.info("No station coordinates available for the current filters.")
            else:
                center_lat = float(station_agg["start_station_latitude"].median())
                center_lon = float(station_agg["start_station_longitude"].median())
                fig = px.scatter_map(
                    station_agg,
                    lat="start_station_latitude", lon="start_station_longitude",
                    size="trips", color="trips", hover_name="start_station_name",
                    hover_data={"trips": True,
                                "start_station_latitude": ":.5f",
                                "start_station_longitude": ":.5f"},
                    zoom=10.5, height=560, title="Trips started at each station",
                    center={"lat": center_lat, "lon": center_lon},
                    size_max=25, opacity=0.8,
                    color_continuous_scale="Viridis", map_style="open-street-map",
                )
                fig.update_layout(
                    map=dict(center=dict(lat=center_lat, lon=center_lon), zoom=10.5)
                )
                show(fig)
                st.caption("Map tiles load from the internet — if the map looks empty, "
                           "check your connection. Marker sizes scale with trip counts.")
        except Exception as exc:
            st.warning(f"Interactive map could not be rendered: {exc}")
            try:
                fallback = (
                    df.groupby(["start_station_name", "start_station_latitude",
                                "start_station_longitude"])
                    .size().rename("trips").reset_index()
                    .dropna(subset=["start_station_latitude", "start_station_longitude"])
                )
                if not fallback.empty:
                    st.info("Showing a tile-free fallback plot (no basemap needed):")
                    fig_fb = px.scatter(
                        fallback, x="start_station_longitude", y="start_station_latitude",
                        size="trips", color="trips", hover_name="start_station_name",
                        title="Station activity (fallback — longitude vs latitude)",
                        labels={"start_station_longitude": "Longitude",
                                "start_station_latitude": "Latitude"},
                        color_continuous_scale="Viridis",
                    )
                    fig_fb.update_yaxes(scaleanchor="x", scaleratio=1)
                    show(fig_fb, height=560)
            except Exception as exc2:
                st.warning(f"Fallback plot also failed: {exc2}")

# ---- Rider Demographics -----------------------------------------------------------
with tab_riders:
    c1, c2 = st.columns(2)
    with c1:
        if df["age"].notna().any():
            fig = px.histogram(
                df.dropna(subset=["age"]), x="age", nbins=30, title="Rider Age Distribution",
                color_discrete_sequence=["#F18F01"],
            )
            fig.update_layout(xaxis_range=[15, 85])
            show(fig, height=340)
            st.caption(f"Most common age: **{int(df['age'].mode().iloc[0])}** · median "
                       f"**{df['age'].median():.0f}**.")
    with c2:
        counts = count_frame(
            df["member_gender"], "gender",
            order=[g for g in GENDER_ORDER if g in df["member_gender"].unique()],
        )
        fig = px.pie(counts, names="gender", values="count", hole=0.45,
                     title="Gender Distribution", color_discrete_sequence=PALETTE)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        show(fig, height=340)
        st.caption("Male riders are the largest group, followed by Female.")

    c3, c4 = st.columns(2)
    with c3:
        if {"member_gender", "duration_min"}.issubset(df.columns):
            fig = px.box(
                df.dropna(subset=["member_gender"]), x="member_gender", y="duration_min",
                color="member_gender", title="Trip Duration by Gender",
                color_discrete_sequence=PALETTE, points=False,
            )
            fig.update_yaxes(range=[0, df["duration_min"].quantile(0.95)])
            show(fig, height=360)
            avg_dur = (
                df.dropna(subset=["member_gender"])
                .groupby("member_gender")["duration_min"]
                .mean()
                .sort_values(ascending=False)
            )
            if not avg_dur.empty:
                summary = " > ".join(f"{g} {v:.1f}" for g, v in avg_dur.items())
                st.caption(f"Average duration: {summary} min.")
    with c4:
        if {"user_type", "age"}.issubset(df.columns):
            fig = px.violin(
                df.dropna(subset=["age"]), x="user_type", y="age", color="user_type",
                box=True, title="Age Distribution by User Type",
                color_discrete_sequence=["#2E86AB", "#F18F01"],
            )
            show(fig, height=360)
            med_age = df.dropna(subset=["age"]).groupby("user_type")["age"].median()
            if not med_age.empty:
                ages = " vs ".join(f"{ut} {v:.0f}" for ut, v in med_age.items())
                st.caption(f"Age profiles are close: median {ages}.")

    if {"user_type", "duration_min"}.issubset(df.columns):
        fig = px.box(
            df, x="user_type", y="duration_min", color="user_type",
            title="Trip Duration by User Type", points=False,
            color_discrete_sequence=["#2E86AB", "#F18F01"],
        )
        fig.update_yaxes(range=[0, df["duration_min"].quantile(0.95)])
        show(fig, height=340)
        means = df.groupby("user_type")["duration_min"].mean()
        if len(means) >= 2:
            meds = df.groupby("user_type")["duration_min"].median()
            longest, shortest = means.idxmax(), means.idxmin()
            st.caption(
                f"{longest} ride considerably longer (mean {means[longest]:.1f} vs "
                f"{means[shortest]:.1f} min; median {meds[longest]:.1f} vs "
                f"{meds[shortest]:.1f} min)."
            )

# ---- Data Quality -------------------------------------------------------------------
with tab_quality:
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows", f"{len(df):,}")
    q2.metric("Columns", f"{df.shape[1]}")
    q3.metric("Missing values", f"{int(df.isna().sum().sum()):,}")
    q4.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Missing values per column")
        miss = df.isna().sum()
        miss = miss[miss > 0].rename("missing").reset_index()
        if miss.empty:
            st.success("No missing values in the filtered rows.")
        else:
            miss.columns = ["column", "missing"]
            st.dataframe(miss, width="stretch", hide_index=True,
                         column_config={
                             "missing": st.column_config.ProgressColumn(
                                 "missing", min_value=0, max_value=int(df.isna().sum().max())
                             )
                         })
    with c2:
        st.subheader("Column types")
        dtypes = df.dtypes.astype(str).rename("dtype").reset_index()
        dtypes.columns = ["column", "dtype"]
        st.dataframe(dtypes, width="stretch", hide_index=True)

    st.subheader("Sample of raw timestamps")
    if "start_time" in df.columns:
        raw_sample = (
            df["start_time"].astype(str).value_counts().head(8)
            .rename_axis("start_time").reset_index(name="count")
        )
        st.dataframe(raw_sample, width="stretch", hide_index=True)
        st.caption("These are the stored values as-is. They contain no date component, "
                   "so they cannot be used for weekday/hour/month analysis.")

# ---- Raw Data ----------------------------------------------------------------------
with tab_data:
    st.dataframe(df, width="stretch", height=500)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data as CSV", csv_bytes,
                       "fordgobike_filtered_trips.csv", "text/csv")