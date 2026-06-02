from datetime import date

import pandas as pd
import streamlit as st
from components.api_client import api_get
from components.auth import require_login

st.title("Dashboard")
require_login()

st.subheader("Merchant orders")
today = date.today()
filter_cols = st.columns(3)
selected_service_date = filter_cols[0].date_input("Order date", value=today)
month_options = ["All months"] + list(range(1, 13))
selected_months = filter_cols[1].multiselect(
    "Month",
    month_options,
    default=[today.month],
    format_func=lambda month: month if isinstance(month, str) else date(2000, month, 1).strftime("%B"),
)
selected_year = filter_cols[2].number_input("Year", min_value=2024, max_value=2035, value=today.year, step=1)

try:
    if "All months" in selected_months:
        month_query = "&months=all"
    else:
        month_values = [str(month) for month in selected_months if isinstance(month, int)]
        month_query = f"&months={','.join(month_values)}" if month_values else ""
    merchant = api_get(
        f"/merchant/dashboard?year={int(selected_year)}&service_date={selected_service_date.isoformat()}{month_query}"
    )
    metric_cols = st.columns(4)
    metric_cols[0].metric("Total orders", merchant["total_orders_for_date"])
    metric_cols[1].metric("Fulfilled orders", merchant["fulfilled_orders_for_date"])
    metric_cols[2].metric("Pending orders", merchant["pending_orders_for_date"])
    metric_cols[3].metric("Total orders next day", merchant["total_orders_next_day"])

    request_cols = st.columns(3)
    request_cols[0].metric("Open Requests", merchant["open_requests"])
    request_cols[1].metric("Accepted requests", merchant["accepted_requests_for_date"])
    request_cols[2].metric("Accepted requests next day", merchant["accepted_requests_next_day"])

    st.subheader("Orders and revenue by day")
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
    chart_df["revenue"] = 0.0

    if daily_metrics:
        metrics_df = pd.DataFrame(daily_metrics)
        metrics_df["day"] = pd.to_datetime(metrics_df["date"])
        metrics_df = metrics_df.set_index("day")[["orders", "revenue"]]
        chart_df.update(metrics_df)

    chart_df = chart_df.reset_index()
    chart_df["day"] = chart_df["day"].dt.strftime("%Y-%m-%d")
    chart_df = chart_df.set_index("day")
    chart_df["orders"] = chart_df["orders"].astype(int)
    chart_df["revenue"] = chart_df["revenue"].astype(float)

    st.caption(f"Filtered by year {int(selected_year)} and selected month filter.")
    st.markdown("**Orders by day**")
    st.bar_chart(chart_df[["orders"]])
    st.markdown("**Revenue by day**")
    st.bar_chart(chart_df[["revenue"]])
    st.dataframe(chart_df.reset_index(), use_container_width=True, hide_index=True)
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
