import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def products_to_dataframe(products):
    rows = []

    for p in products:
        rows.append({
            "ID": p[0],
            "Title": p[1],
            "Category": p[2],
            "Photo": p[3],
            "Cropped Photo": p[4],
            "QR Code": p[5],
            "Base Price": p[6],
            "Average Market Price": p[7],
            "Damage %": p[8],
            "Final Price": p[9],
            "Status": p[10],
            "Created At": p[11],
            "Sold At": p[12],
        })

    return pd.DataFrame(rows)


def export_excel(products, filename):
    df = products_to_dataframe(products)
    df.to_excel(filename, index=False)
    return filename


def export_pdf(products, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Kringloop Products Export")

    y -= 40
    c.setFont("Helvetica", 10)

    for p in products:
        text = f"ID: {p[0]} | {p[1]} | {p[2]} | €{p[9]} | {p[10]}"
        c.drawString(50, y, text)
        y -= 20

        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    c.save()
    return filename