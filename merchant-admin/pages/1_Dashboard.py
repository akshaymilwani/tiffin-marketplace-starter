from datetime import date

import altair as alt
import pandas as pd
import streamlit as st
from components.api_client import api_get
from components.auth import require_login

st.title("Dashboard")
require_login()

st.subheader("Merchant orders")
today = date.today()
selected_service_date = st.date_input("Order date", value=today)
metrics_container = st.container()

st.subheader("Orders and revenue by day")
chart_filter_cols = st.columns(2)
month_options = ["All months"] + list(range(1, 13))
selected_months = chart_filter_cols[0].multiselect(
    "Month",
    month_options,
    default=[selected_service_date.month],
    format_func=lambda month: month if isinstance(month, str) else date(2000, month, 1).strftime("%B"),
)
selected_year = chart_filter_cols[1].number_input(
    "Year",
    min_value=2024,
    max_value=2035,
    value=selected_service_date.year,
    step=1,
)

try:
    if "All months" in selected_months:
        month_query = "&months=all"
    else:
        month_values = [str(month) for month in selected_months if isinstance(month, int)]
        month_query = f"&months={','.join(month_values)}" if month_values else ""
    merchant = api_get(
        f"/merchant/dashboard?year={int(selected_year)}&service_date={selected_service_date.isoformat()}{month_query}"
    )

    with metrics_container:
        order_cols = st.columns(4)
        order_cols[0].metric("Total orders received", merchant["total_orders_for_date"])
        order_cols[1].metric("Accepted orders", merchant["accepted_orders_for_date"])
        order_cols[2].metric("Fulfilled orders", merchant["fulfilled_orders_for_date"])
        order_cols[3].metric("Pending orders", merchant["pending_orders_for_date"])

        request_cols = st.columns(4)
        request_cols[0].metric("Open Requests", merchant["open_requests"])
        request_cols[1].metric("Accepted requests", merchant["accepted_requests_for_date"])
        request_cols[2].metric("Fulfilled requests", merchant["fulfilled_requests_for_date"])
        request_cols[3].metric("Accepted requests next day", merchant["accepted_requests_next_day"])

    daily_metrics = merchant.get("daily_metrics", [])
    if "All months" in selected_months:
        selected_month_numbers = list(range(1, 13))
    else:
        selected_month_numbers = [month for month in selected_months if isinstance(month, int)]
    if not selected_month_numbers:
        selected_month_numbers = [today.month]

    date_indexes = [
        pd.date_range(
            start=date(int(selected_year), month_number, 1),
            end=pd.Period(f"{int(selected_year)}-{month_number:02d}").end_time.date(),
            freq="D",
        )
        for month_number in selected_month_numbers
    ]
    full_dates = date_indexes[0]
    for date_index in date_indexes[1:]:
        full_dates = full_dates.append(date_index)

    chart_df = pd.DataFrame(index=full_dates)
    chart_df.index.name = "day"
    chart_df["orders"] = 0
    chart_df["fulfilled_orders"] = 0
    chart_df["fulfilled_requests"] = 0
    chart_df["revenue"] = 0.0

    if daily_metrics:
        metrics_df = pd.DataFrame(daily_metrics)
        metrics_df["day"] = pd.to_datetime(metrics_df["date"])
        metrics_df = metrics_df.set_index("day")[["orders", "fulfilled_orders", "fulfilled_requests", "revenue"]]
        chart_df.update(metrics_df)

    chart_df = chart_df.reset_index()
    chart_df["day"] = chart_df["day"].dt.strftime("%Y-%m-%d")
    chart_df = chart_df.set_index("day")
    chart_df["orders"] = chart_df["orders"].clip(lower=0).round().astype(int)
    chart_df["fulfilled_orders"] = chart_df["fulfilled_orders"].clip(lower=0).round().astype(int)
    chart_df["fulfilled_requests"] = chart_df["fulfilled_requests"].clip(lower=0).round().astype(int)
    chart_df["revenue"] = chart_df["revenue"].clip(lower=0).round().astype(int)

    table_df = chart_df.reset_index()
    order_chart_df = table_df.melt(
        id_vars=["day"],
        value_vars=["fulfilled_orders", "fulfilled_requests"],
        var_name="Type",
        value_name="Count",
    )
    order_chart_df["Type"] = order_chart_df["Type"].replace(
        {
            "fulfilled_orders": "Fulfilled orders",
            "fulfilled_requests": "Fulfilled requests",
        }
    )
    revenue_chart_df = table_df[["day", "revenue"]].rename(columns={"revenue": "Revenue"})

    st.caption(f"Filtered by year {int(selected_year)} and selected month filter.")
    st.markdown("**Orders fulfilled (including request)**")
    order_chart = (
        alt.Chart(order_chart_df)
        .mark_bar()
        .encode(
            x=alt.X("day:N", title="Date", sort=None),
            y=alt.Y("Count:Q", title="Orders fulfilled", scale=alt.Scale(domainMin=0), axis=alt.Axis(format="d")),
            color=alt.Color("Type:N", title="Type"),
            tooltip=["day", "Type", "Count"],
        )
        .properties(height=320)
    )
    st.altair_chart(order_chart, use_container_width=True)

    st.markdown("**Earned Revenue**")
    revenue_chart = (
        alt.Chart(revenue_chart_df)
        .mark_bar()
        .encode(
            x=alt.X("day:N", title="Date", sort=None),
            y=alt.Y("Revenue:Q", title="Earned revenue", scale=alt.Scale(domainMin=0), axis=alt.Axis(format="d")),
            tooltip=["day", "Revenue"],
        )
        .properties(height=320)
    )
    st.altair_chart(revenue_chart, use_container_width=True)

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    total_cols = st.columns(4)
    total_fulfilled_orders = int(chart_df["fulfilled_orders"].sum())
    total_fulfilled_requests = int(chart_df["fulfilled_requests"].sum())
    total_cols[0].metric("Total fulfilled orders", total_fulfilled_orders)
    total_cols[1].metric("Total fulfilled requests", total_fulfilled_requests)
    total_cols[2].metric("Total fulfilled including requests", total_fulfilled_orders + total_fulfilled_requests)
    total_cols[3].metric("Total earned revenue", f"${int(chart_df['revenue'].sum())}")
except Exception as e:
    st.warning("Create a business profile before using the merchant dashboard.")
    st.exception(e)

if st.session_state.get("role") == "admin":
    st.subheader("Admin snapshot")
    try:
        admin = api_get("/admin/dashboard")
        metric_cols = st.columns(3)
        metric_cols[0].metric("Pending verifications", admin["pending_verifications"])
        metric_cols[1].metric("Visible merchants", admin["active_merchants"])
        metric_cols[2].metric("Expired subscriptions", admin["expired_subscriptions"])
    except Exception as e:
        st.exception(e)
