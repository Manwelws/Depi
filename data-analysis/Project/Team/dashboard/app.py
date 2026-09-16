import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def scatter_on_map(*, lat, lon, size, color, hover_name, zoom, height, title, color_continuous_scale, data_frame):
    fig = px.scatter_map(
            data_frame, lat=lat, lon=lon, size=size, color=color, hover_name=hover_name,
            zoom=zoom, height=height, map_style="carto-positron",
            title=title, color_continuous_scale=color_continuous_scale,
        )
    return fig

# ------------------------------------------------Fix the attached problem--------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Bike Share Trip Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Data loading & caching
# --------------------------------------------------------------------------
EXPECTED_COLS = [
    "duration_sec", "start_time", "end_time",
    "start_station_id", "start_station_name", "start_station_latitude", "start_station_longitude",
    "end_station_id", "end_station_name", "end_station_latitude", "end_station_longitude",
    "bike_id", "user_type", "member_birth_year", "member_gender", "bike_share_for_all_trip",
]


@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    return df


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    has_start_time = "start_time" in df.columns
    has_end_time = "end_time" in df.columns
    if has_start_time:
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    if has_end_time:
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
    if "duration_sec" in df.columns:
        df["duration_min"] = pd.to_numeric(df["duration_sec"], errors="coerce") / 60.0

    # Age at time of trip = year of the trip minus birth year.
    # Only computed when both a usable start_time and a birth year exist.
    if "member_birth_year" in df.columns and has_start_time and df["start_time"].notna().any():
        trip_year = df["start_time"].dt.year
        fallback_year = trip_year.median()  # used only for rows with an unparsable start_time
        df["member_age"] = trip_year.fillna(fallback_year) - pd.to_numeric(df["member_birth_year"], errors="coerce")
        # Drop implausible ages (bad birth-year entries) rather than plotting them
        df.loc[(df["member_age"] < 10) | (df["member_age"] > 100), "member_age"] = np.nan

    # Time-based features
    if has_start_time and df["start_time"].notna().any():
        df["hour"] = df["start_time"].dt.hour
        df["day_of_week"] = df["start_time"].dt.day_name()
        df["date"] = df["start_time"].dt.date
        df["month"] = df["start_time"].dt.to_period("M").astype(str)

    # Round-trip flag — only meaningful if both station-id columns are present
    if {"start_station_id", "end_station_id"}.issubset(df.columns):
        df["same_station_trip"] = df["start_station_id"] == df["end_station_id"]

    return df


DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --------------------------------------------------------------------------
# Sidebar — data source & filters
# --------------------------------------------------------------------------
st.sidebar.title("🚲 Dashboard Controls")

try:
    raw_df = load_csv("/home/manwelw/depi/Depi/data-analysis/Project/Team/arwa/cleaned_fordgobike.csv")
except Exception as e:
    st.error(f"Couldn't read that file as CSV: {e}")
    st.stop()

if raw_df.empty:
    st.error("The file has no rows.")
    st.stop()

st.sidebar.success(f"Loaded {len(raw_df):,} rows.")

missing = [c for c in EXPECTED_COLS if c not in raw_df.columns]
if missing:
    st.sidebar.warning(f"Missing expected columns: {', '.join(missing)}")

df = clean_and_enrich(raw_df)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

# Date range filter
if "start_time" in df.columns and df["start_time"].notna().any():
    min_date = df["start_time"].min().date()
    max_date = df["start_time"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
        df = df[(df["start_time"].dt.date >= start_d) & (df["start_time"].dt.date <= end_d)]

# User type filter
if "user_type" in df.columns:
    user_types = sorted(df["user_type"].dropna().unique().tolist())
    sel_user_types = st.sidebar.multiselect("User type", user_types, default=user_types)
    df = df[df["user_type"].isin(sel_user_types)]

# Gender filter
if "member_gender" in df.columns:
    genders = sorted(df["member_gender"].dropna().unique().tolist())
    sel_genders = st.sidebar.multiselect("Gender", genders, default=genders)
    df = df[df["member_gender"].isin(sel_genders)]

# Duration filter — full range is selectable; default view excludes the top 1%
# of outliers (common in bike-share data, e.g. bikes left out overnight) but
# the user can still drag up to the true max.
if "duration_min" in df.columns and df["duration_min"].notna().any():
    true_min = float(np.floor(df["duration_min"].min()))
    true_max = float(np.ceil(df["duration_min"].max()))
    default_max = float(np.ceil(df["duration_min"].quantile(0.99)))
    if true_max > true_min:
        dur_range = st.sidebar.slider(
            "Trip duration (minutes)", true_min, true_max, (true_min, min(default_max, true_max))
        )
        df = df[(df["duration_min"] >= dur_range[0]) & (df["duration_min"] <= dur_range[1])]

st.sidebar.markdown("---")
st.sidebar.caption(f"Rows after filtering: **{len(df):,}**")

# --------------------------------------------------------------------------
# Header & KPIs
# --------------------------------------------------------------------------
st.title("🚲 Bike Share Trip Data — Interactive Dashboard")
st.caption(f"Ford GoBike")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Trips", f"{len(df):,}")
if "duration_min" in df.columns:
    k2.metric("Avg Duration", f"{df['duration_min'].mean():.1f} min")
    k3.metric("Median Duration", f"{df['duration_min'].median():.1f} min")
if "bike_id" in df.columns:
    k4.metric("Unique Bikes", f"{df['bike_id'].nunique():,}")
if "user_type" in df.columns and len(df) > 0:
    subs_pct = (df["user_type"].eq("Subscriber").mean() * 100) if "Subscriber" in df["user_type"].unique() else np.nan
    k5.metric("Subscriber %", f"{subs_pct:.1f}%" if not np.isnan(subs_pct) else "N/A")

st.markdown("---")

if len(df) == 0:
    st.warning("No trips match the current filters. Try widening your selection.")
    st.stop()

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_overview, tab_time, tab_stations, tab_riders, tab_data = st.tabs(
    ["📊 Overview", "🕒 Time Patterns", "📍 Stations & Map", "🧑 Rider Demographics", "🗂️ Raw Data"]
)

# ---- Overview ----
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        if "duration_min" in df.columns:
            fig = px.histogram(
                df[df["duration_min"] < df["duration_min"].quantile(0.98)],
                x="duration_min", nbins=40,
                title="Trip Duration Distribution",
                labels={"duration_min": "Duration (minutes)"},
                color_discrete_sequence=["#2E86AB"],
            )
            fig.update_layout(bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "user_type" in df.columns:
            counts = df["user_type"].value_counts().reset_index()
            counts.columns = ["user_type", "count"]
            fig = px.pie(
                counts, names="user_type", values="count", hole=0.45,
                title="User Type Split",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        if "bike_share_for_all_trip" in df.columns:
            counts = df["bike_share_for_all_trip"].value_counts().reset_index()
            counts.columns = ["bike_share_for_all_trip", "count"]
            fig = px.bar(
                counts, x="bike_share_for_all_trip", y="count",
                title="Bike Share For All Trips",
                color="bike_share_for_all_trip",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if "same_station_trip" in df.columns:
            counts = df["same_station_trip"].map({True: "Round trip", False: "One-way"}).value_counts().reset_index()
            counts.columns = ["trip_type", "count"]
            fig = px.bar(
                counts, x="trip_type", y="count",
                title="Round Trip vs One-Way",
                color="trip_type",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ---- Time Patterns ----
with tab_time:
    if "date" in df.columns:
        daily = df.groupby("date").size().reset_index(name="trips")
        fig = px.line(daily, x="date", y="trips", title="Trips Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if "hour" in df.columns:
            hourly = df.groupby("hour").size().reindex(range(24), fill_value=0).reset_index(name="trips")
            hourly.columns = ["hour", "trips"]
            fig = px.bar(hourly, x="hour", y="trips", title="Trips by Hour of Day")
            fig.update_layout(xaxis=dict(dtick=1))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "day_of_week" in df.columns:
            dow = df.groupby("day_of_week").size().reindex(DOW_ORDER, fill_value=0).reset_index(name="trips")
            dow.columns = ["day_of_week", "trips"]
            fig = px.bar(dow, x="day_of_week", y="trips", title="Trips by Day of Week")
            st.plotly_chart(fig, use_container_width=True)

    if "hour" in df.columns and "day_of_week" in df.columns:
        heat = df.groupby(["day_of_week", "hour"]).size().reset_index(name="trips")
        heat_pivot = heat.pivot(index="day_of_week", columns="hour", values="trips").reindex(DOW_ORDER)
        fig = px.imshow(
            heat_pivot, aspect="auto",
            title="Trip Volume Heatmap (Day of Week × Hour)",
            labels=dict(x="Hour", y="Day of Week", color="Trips"),
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

# ---- Stations & Map ----
with tab_stations:
    c1, c2 = st.columns(2)
    with c1:
        if "start_station_name" in df.columns:
            top_start = df["start_station_name"].value_counts().head(10).reset_index()
            top_start.columns = ["station", "trips"]
            fig = px.bar(
                top_start.sort_values("trips"), x="trips", y="station", orientation="h",
                title="Top 10 Start Stations",
                color_discrete_sequence=["#2E86AB"],
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "end_station_name" in df.columns:
            top_end = df["end_station_name"].value_counts().head(10).reset_index()
            top_end.columns = ["station", "trips"]
            fig = px.bar(
                top_end.sort_values("trips"), x="trips", y="station", orientation="h",
                title="Top 10 End Stations",
                color_discrete_sequence=["#A23B72"],
            )
            st.plotly_chart(fig, use_container_width=True)

    if {"start_station_latitude", "start_station_longitude", "start_station_name"}.issubset(df.columns):
        station_agg = (
            df.groupby(["start_station_name", "start_station_latitude", "start_station_longitude"])
            .size().reset_index(name="trips")
        )
        fig = scatter_on_map(
            data_frame=station_agg,
            lat="start_station_latitude", lon="start_station_longitude",
            size="trips", color="trips", hover_name="start_station_name",
            zoom=11, height=550,
            title="Station Activity Map (by start-trip volume)",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

# ---- Rider Demographics ----
with tab_riders:
    c1, c2 = st.columns(2)
    with c1:
        if "member_age" in df.columns and df["member_age"].notna().any():
            fig = px.histogram(
                df.dropna(subset=["member_age"]), x="member_age", nbins=30,
                title="Rider Age Distribution", color_discrete_sequence=["#F18F01"],
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "member_gender" in df.columns:
            counts = df["member_gender"].value_counts().reset_index()
            counts.columns = ["gender", "count"]
            fig = px.pie(
                counts, names="gender", values="count", hole=0.45,
                title="Gender Distribution", color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, use_container_width=True)

    if {"member_gender", "duration_min"}.issubset(df.columns):
        fig = px.box(
            df, x="member_gender", y="duration_min", color="member_gender",
            title="Trip Duration by Gender",
            points=False,
        )
        fig.update_yaxes(range=[0, df["duration_min"].quantile(0.95)])
        st.plotly_chart(fig, use_container_width=True)

    if {"user_type", "member_age"}.issubset(df.columns):
        fig = px.violin(
            df.dropna(subset=["member_age"]), x="user_type", y="member_age", color="user_type",
            box=True, title="Age Distribution by User Type",
        )
        st.plotly_chart(fig, use_container_width=True)

# ---- Raw Data ----
with tab_data:
    st.dataframe(df, use_container_width=True, height=500)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv_bytes, "filtered_trips.csv", "text/csv")