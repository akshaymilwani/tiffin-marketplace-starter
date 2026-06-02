import streamlit as st

from components.auth import require_login
from components.business_context import require_business
from components.api_client import api_get, api_put

st.title("Orders Inbox")
require_login()
require_business()

status_filter = st.selectbox("Status", ["all", "pending", "accepted", "fulfilled", "rejected", "cancelled"])
path = "/merchant/orders" if status_filter == "all" else f"/merchant/orders?status={status_filter}"

try:
    orders = api_get(path)
except Exception as e:
    st.error("Failed to load orders.")
    st.exception(e)
    st.stop()

if not orders:
    st.info("No orders found.")
    st.stop()

summary = [
    {
        "order_number": order["order_number"],
        "status": order["status"],
        "service_date": order["service_date"],
        "slot": order["slot_type"],
        "fulfillment": order["fulfillment_mode"],
        "total": order["total_amount"],
        "items": sum(item["quantity"] for item in order["items"]),
    }
    for order in orders
]
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Order details")
for order in orders:
    with st.expander(f"{order['order_number']} - {order['status']} - ${order['total_amount']:.2f}"):
        st.write(f"Service: {order['service_date']} / {order['slot_type']}")
        st.write(f"Fulfillment: {order['fulfillment_mode']}")
        if order.get("customer_notes"):
            st.write(f"Customer notes: {order['customer_notes']}")
        st.dataframe(order["items"], use_container_width=True, hide_index=True)

        merchant_notes = st.text_area("Merchant notes", value=order.get("merchant_notes") or "", key=f"notes_{order['id']}")
        cols = st.columns(4)
        fulfilled_label = "Mark picked up" if order.get("fulfillment_mode") == "pickup" else "Fulfill"
        actions = [("Accept", "accepted"), ("Reject", "rejected"), (fulfilled_label, "fulfilled"), ("Cancel", "cancelled")]
        for col, (label, status) in zip(cols, actions):
            if col.button(label, key=f"{status}_{order['id']}"):
                try:
                    api_put(
                        f"/merchant/orders/{order['id']}/status",
                        {"status": status, "merchant_notes": merchant_notes},
                    )
                    st.success(f"Order marked {status}.")
                    st.rerun()
                except Exception as e:
                    st.exception(e)
