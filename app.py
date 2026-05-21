from google_lens_helper import upload_image_and_create_google_lens_link
from image_price_search import parse_manual_prices

import os
from datetime import datetime

import qrcode
import streamlit as st
from PIL import Image
from rembg import remove
from streamlit_cropper import st_cropper

from database import init_db, add_product, get_products, mark_as_sold
from pricing import calculate_final_price
from export_tools import export_excel, export_pdf


init_db()

st.set_page_config(page_title="Kringloop Pricing App", layout="wide")
st.title("Kringloop Product Pricing System")


def ensure_folders_exist():
    for folder in ["uploads", "cropped", "labels", "exports"]:
        os.makedirs(folder, exist_ok=True)


def safe_filename(original_name):
    name = os.path.basename(original_name)
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f_") + name


def save_image(image, folder, original_name):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, safe_filename(original_name))
    image.save(path)
    return path


def create_qr_label(product_name, price):
    os.makedirs("labels", exist_ok=True)

    qr_text = f"Product: {product_name}\nPrice: €{price}"
    qr = qrcode.make(qr_text)

    path = os.path.join(
        "labels",
        datetime.now().strftime("%Y%m%d_%H%M%S_%f_") + "qr.png"
    )

    qr.save(path)
    return path


ensure_folders_exist()


page = st.sidebar.selectbox(
    "Choose page",
    ["Add Product", "Inventory", "Sold Products", "Export"],
    key="main_page_selectbox"
)


if page == "Add Product":
    st.header("Add New Product")

    title = st.text_input("Product name", key="product_name_input")

    category = st.selectbox(
        "Category",
        ["Clothing", "Furniture", "Electronics", "Books", "Kitchen", "Other"],
        key="category_selectbox"
    )

    uploaded_file = st.file_uploader(
        "Upload product photo",
        type=["jpg", "jpeg", "png"],
        key="product_photo_uploader"
    )

    image = None
    final_image = None

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")

        st.subheader("1. Crop Image")

        cropped_image = st_cropper(
            image,
            realtime_update=True,
            box_color="#FF0000",
            aspect_ratio=None,
            key="image_cropper"
        )

        st.image(cropped_image, caption="Cropped image", width=300)

        st.subheader("2. Background Removal")

        remove_bg = st.checkbox(
            "Remove background automatically",
            key="remove_background_checkbox"
        )

        if remove_bg:
            with st.spinner("Removing background..."):
                no_bg = remove(cropped_image)
                final_image = no_bg.convert("RGB")

            st.image(final_image, caption="Background removed", width=300)
        else:
            final_image = cropped_image
    else:
        st.info("Upload a product photo first.")

    st.subheader("3. Google Lens Price Check")

    st.write(
        "Click the button below to upload the cropped product photo and open Google Lens. "
        "Then copy prices from Google Lens / Marktplaats / bol.com / Coolblue / MediaMarkt / Amazon.nl "
        "and paste them in the manual price box."
    )

    if uploaded_file and final_image is not None:
        if st.button("Create Google Lens Search", key="create_google_lens_button"):
            temp_search_path = save_image(
                final_image,
                "cropped",
                uploaded_file.name
            )

            with st.spinner("Uploading image and creating Google Lens link..."):
                image_url, google_lens_url = upload_image_and_create_google_lens_link(
                    temp_search_path
                )

            st.session_state["google_lens_image_url"] = image_url
            st.session_state["google_lens_url"] = google_lens_url

        image_url = st.session_state.get("google_lens_image_url", "")
        google_lens_url = st.session_state.get("google_lens_url", "")

        if image_url:
            st.image(image_url, caption="Image uploaded for Google Lens", width=250)

        if google_lens_url:
            st.link_button("Open Google Lens Search", google_lens_url)
    else:
        st.warning("Please upload and crop an image before creating Google Lens search.")

    st.subheader("4. Price Input")

    price_text = st.text_input(
        "Enter prices you found, separated by comma",
        placeholder="Example: 20, 25, 30, 35",
        key="manual_prices_input"
    )

    avg_market_price = parse_manual_prices(price_text)

    st.metric("Average entered price", f"€{avg_market_price}")

    st.subheader("5. Price Adjustment")

    price_source = st.radio(
        "Choose base price",
        ["Use average entered price", "Enter base price manually"],
        key="base_price_source_radio"
    )

    if price_source == "Use average entered price":
        base_price = float(avg_market_price)
    else:
        base_price = st.number_input(
            "Manual base price",
            min_value=0.0,
            step=1.0,
            key="manual_base_price_input"
        )

    adjust_percent = st.slider(
        "Adjust price up or down",
        min_value=-50,
        max_value=50,
        value=0,
        help="Negative means cheaper. Positive means more expensive.",
        key="adjust_price_slider"
    )

    adjusted_price = base_price * (1 + adjust_percent / 100)

    damage_percent = st.slider(
        "Damage / wear percentage",
        min_value=0,
        max_value=100,
        value=10,
        key="damage_percent_slider"
    )

    calculated_price = calculate_final_price(adjusted_price, damage_percent)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Base price", f"€{round(base_price, 2)}")

    with col_b:
        st.metric("Adjusted price", f"€{round(adjusted_price, 2)}")

    with col_c:
        st.metric("Calculated final price", f"€{calculated_price}")

    manual_override = st.checkbox(
        "Enter final price manually",
        key="manual_final_price_checkbox"
    )

    if manual_override:
        final_price = st.number_input(
            "Manual final price",
            min_value=0.0,
            step=1.0,
            key="manual_final_price_input"
        )
    else:
        final_price = calculated_price

    st.write("### Final price:", f"€{final_price}")

    if st.button("Save Product", key="save_product_button"):
        if not title:
            st.error("Please enter product name.")
        elif not uploaded_file:
            st.error("Please upload a photo.")
        elif final_image is None:
            st.error("Please crop/select the image first.")
        else:
            original_path = save_image(image, "uploads", uploaded_file.name)
            cropped_path = save_image(final_image, "cropped", uploaded_file.name)
            qr_path = create_qr_label(title, final_price)

            add_product(
                title,
                category,
                original_path,
                cropped_path,
                qr_path,
                base_price,
                avg_market_price,
                damage_percent,
                final_price
            )

            st.success("Product saved successfully!")
            st.image(qr_path, caption="QR Label", width=150)


elif page == "Inventory":
    st.header("Products in Warehouse")

    products = get_products(status="in_stock")

    if not products:
        st.info("No products in stock.")
    else:
        for product in products:
            product_id = product[0]
            title = product[1]
            category = product[2]
            cropped_photo_path = product[4]
            qr_path = product[5]
            base_price = product[6]
            avg_market_price = product[7]
            damage_percent = product[8]
            final_price = product[9]

            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if cropped_photo_path and os.path.exists(cropped_photo_path):
                    st.image(cropped_photo_path, width=150)

                if qr_path and os.path.exists(qr_path):
                    st.image(qr_path, caption="QR", width=100)

            with col2:
                st.subheader(title)
                st.write("Category:", category)
                st.write("Base price:", base_price)
                st.write("Average market price:", avg_market_price)
                st.write("Damage:", str(damage_percent) + "%")
                st.write("Final price:", final_price)

            with col3:
                if st.button("Mark as Sold", key=f"sold_button_{product_id}"):
                    mark_as_sold(product_id)
                    st.success("Product marked as sold.")
                    st.rerun()

            st.divider()


elif page == "Sold Products":
    st.header("Sold Products")

    products = get_products(status="sold")

    if not products:
        st.info("No sold products yet.")
    else:
        for product in products:
            title = product[1]
            category = product[2]
            cropped_photo_path = product[4]
            final_price = product[9]
            sold_at = product[12]

            col1, col2 = st.columns([1, 3])

            with col1:
                if cropped_photo_path and os.path.exists(cropped_photo_path):
                    st.image(cropped_photo_path, width=150)

            with col2:
                st.subheader(title)
                st.write("Category:", category)
                st.write("Sold price:", final_price)
                st.write("Sold at:", sold_at)

            st.divider()


elif page == "Export":
    st.header("Export Products")

    export_type = st.radio(
        "Which products do you want to export?",
        ["All", "In Stock", "Sold"],
        key="export_type_radio"
    )

    if export_type == "All":
        products = get_products()
    elif export_type == "In Stock":
        products = get_products(status="in_stock")
    else:
        products = get_products(status="sold")

    st.write("Number of products:", len(products))

    excel_path = "exports/products_export.xlsx"
    pdf_path = "exports/products_export.pdf"

    if st.button("Create Excel Export", key="create_excel_export_button"):
        export_excel(products, excel_path)

        with open(excel_path, "rb") as file:
            st.download_button(
                "Download Excel",
                file,
                file_name="products_export.xlsx",
                key="download_excel_button"
            )

    if st.button("Create PDF Export", key="create_pdf_export_button"):
        export_pdf(products, pdf_path)

        with open(pdf_path, "rb") as file:
            st.download_button(
                "Download PDF",
                file,
                file_name="products_export.pdf",
                key="download_pdf_button"
            )