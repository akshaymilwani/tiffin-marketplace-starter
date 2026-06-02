from io import BytesIO

import pandas as pd
import streamlit as st

from components.auth import require_login
from components.business_context import require_business
from components.api_client import api_get, api_post, api_put

st.set_page_config(page_title="Menu Management", layout="wide")

require_login()
business_id = require_business()

st.title("Menu Management")
st.caption(f"Business ID loaded automatically: {business_id}")


def _split_list(value):
    if pd.isna(value) or value is None:
        return []
    if isinstance(value, list):
        return value
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _to_bool(value, default=True):
    if pd.isna(value) or value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "y", "1", "active"}


def _template_bytes():
    template = pd.DataFrame(
        [
            {
                "name": "Dal Tadka",
                "description": "Home-style dal with rice or roti",
                "price": 10.0,
                "cuisine_tag": "Indian",
                "dietary_tags": "vegetarian",
                "spice_level": "medium",
                "prep_lead_time_hours": 4,
                "available_days": "mon,tue,wed,thu,fri",
                "available_slots": "lunch,dinner",
                "is_active": True,
            }
        ]
    )
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        template.to_excel(writer, index=False, sheet_name="menu")
    output.seek(0)
    return output.getvalue()


st.subheader("Update menu from Excel")
st.download_button(
    "Download menu template",
    data=_template_bytes(),
    file_name="menu_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
uploaded_menu = st.file_uploader("Upload menu Excel file", type=["xlsx", "csv"])

if uploaded_menu is not None:
    try:
        if uploaded_menu.name.lower().endswith(".csv"):
            upload_df = pd.read_csv(uploaded_menu)
        else:
            upload_df = pd.read_excel(uploaded_menu)

        st.dataframe(upload_df, use_container_width=True, hide_index=True)

        if st.button("Import uploaded menu"):
            existing_items = api_get("/merchant/menu-items")
            existing_by_name = {item["name"].strip().lower(): item for item in existing_items}
            created_count = 0
            updated_count = 0

            for _, row in upload_df.iterrows():
                name_value = row.get("name")
                if pd.isna(name_value) or not str(name_value).strip():
                    continue

                payload = {
                    "name": str(name_value).strip(),
                    "description": "" if pd.isna(row.get("description")) else str(row.get("description") or ""),
                    "price": float(row.get("price") or 0),
                    "cuisine_tag": "" if pd.isna(row.get("cuisine_tag")) else str(row.get("cuisine_tag") or ""),
                    "dietary_tags": _split_list(row.get("dietary_tags")),
                    "spice_level": "" if pd.isna(row.get("spice_level")) else str(row.get("spice_level") or ""),
                    "prep_lead_time_hours": int(row.get("prep_lead_time_hours") or 0),
                    "available_days": _split_list(row.get("available_days")),
                    "available_slots": _split_list(row.get("available_slots")),
                    "is_active": _to_bool(row.get("is_active"), default=True),
                }

                existing = existing_by_name.get(payload["name"].lower())
                if existing:
                    api_put(f"/merchant/menu-items/{existing['id']}", payload)
                    updated_count += 1
                else:
                    api_post("/menu-items", {"business_id": business_id, **payload})
                    created_count += 1

            st.success(f"Menu import complete. Created {created_count}, updated {updated_count}.")
            st.rerun()
    except Exception as e:
        st.error("Failed to import menu file.")
        st.exception(e)

with st.form("menu_item_form"):
    name = st.text_input("Item Name", placeholder="Dal Tadka")
    description = st.text_area("Description", placeholder="Home-style dal with rice/roti option")
    price = st.number_input("Price", min_value=0.0, step=0.50, value=10.00)
    cuisine_tag = st.text_input("Cuisine Tag", value="Indian")
    dietary_tags_text = st.text_input("Dietary Tags comma-separated", value="vegetarian")
    spice_level = st.selectbox("Spice Level", ["mild", "medium", "spicy"])
    prep_lead_time_hours = st.number_input("Prep Lead Time Hours", min_value=0, step=1, value=4)
    available_days = st.multiselect(
        "Available Days",
        ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        default=["mon", "tue", "wed", "thu", "fri"],
    )
    available_slots = st.multiselect("Available Slots", ["lunch", "dinner"], default=["lunch", "dinner"])
    submitted = st.form_submit_button("Add Menu Item")

if submitted:
    if not name:
        st.error("Item name is required.")
        st.stop()

    try:
        result = api_post(
            "/menu-items",
            {
                "business_id": business_id,
                "name": name,
                "description": description,
                "price": price,
                "cuisine_tag": cuisine_tag,
                "dietary_tags": [tag.strip() for tag in dietary_tags_text.split(",") if tag.strip()],
                "spice_level": spice_level,
                "prep_lead_time_hours": prep_lead_time_hours,
                "available_days": available_days,
                "available_slots": available_slots,
            },
        )
        st.success("Menu item added successfully.")
        st.json(result)
        st.rerun()
    except Exception as e:
        st.error("Failed to add menu item.")
        st.exception(e)

st.subheader("Current menu")
try:
    items = api_get("/merchant/menu-items")
except Exception as e:
    st.exception(e)
    st.stop()

if not items:
    st.info("No menu items yet.")
else:
    st.dataframe(
        [
            {
                "name": item["name"],
                "price": item["price"],
                "active": item["is_active"],
                "slots": ", ".join(item["available_slots"]),
                "days": ", ".join(item["available_days"]),
            }
            for item in items
        ],
        use_container_width=True,
        hide_index=True,
    )

    for item in items:
        with st.expander(f"Edit {item['name']}"):
            with st.form(f"edit_{item['id']}"):
                edit_name = st.text_input("Name", value=item["name"])
                edit_description = st.text_area("Description", value=item.get("description") or "")
                edit_price = st.number_input("Price", min_value=0.0, step=0.50, value=float(item["price"]), key=f"price_{item['id']}")
                edit_active = st.checkbox("Active", value=item["is_active"])
                edit_slots = st.multiselect("Available Slots", ["lunch", "dinner"], default=item.get("available_slots") or [])
                save_item = st.form_submit_button("Save item")

            if save_item:
                try:
                    api_put(
                        f"/merchant/menu-items/{item['id']}",
                        {
                            "name": edit_name,
                            "description": edit_description,
                            "price": edit_price,
                            "is_active": edit_active,
                            "available_slots": edit_slots,
                        },
                    )
                    st.success("Menu item updated.")
                    st.rerun()
                except Exception as e:
                    st.exception(e)
