import pandas as pd
import os
from datetime import datetime


def export_to_csv(data: list, filepath: str = None) -> str:
    """
    Export data berita ke file CSV.
    
    Args:
        data: List of dict berisi data berita
              Format: [{"title": ..., "date": ..., "content": ..., "url": ...}]
        filepath: Path file output (opsional, auto-generate jika kosong)
    
    Returns:
        filepath: Path file yang berhasil disimpan
    """
    if not data:
        raise ValueError("Data kosong, tidak ada yang di-export.")

    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"hasil_berita_{timestamp}.csv"

    folder = os.path.dirname(filepath)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    df = pd.DataFrame(data)

    for col in ["title", "date", "content", "url"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["title", "date", "content", "url"]]
    df.to_csv(filepath, index=False, encoding="utf-8-sig")

    return filepath


def export_to_excel(data: list, filepath: str = None) -> str:
    """
    Export data berita ke file Excel (.xlsx).
    
    Args:
        data: List of dict berisi data berita
        filepath: Path file output (opsional, auto-generate jika kosong)
    
    Returns:
        filepath: Path file yang berhasil disimpan
    """
    if not data:
        raise ValueError("Data kosong, tidak ada yang di-export.")

    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"hasil_berita_{timestamp}.xlsx"

    folder = os.path.dirname(filepath)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    df = pd.DataFrame(data)

    for col in ["title", "date", "content", "url"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["title", "date", "content", "url"]]

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Hasil Berita")

        worksheet = writer.sheets["Hasil Berita"]
        for col_cells in worksheet.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col_cells)
            col_letter = col_cells[0].column_letter
            worksheet.column_dimensions[col_letter].width = min(max_len + 4, 60)

    return filepath


def export_data(data: list, format: str = "csv", filepath: str = None) -> str:
    """
    Fungsi utama export - dipanggil oleh modul lain.
    
    Args:
        data: List of dict berisi data berita
        format: "csv" atau "excel"
        filepath: Path file output (opsional)
    
    Returns:
        filepath: Path file yang berhasil disimpan
    """
    format = format.lower().strip()

    if format == "csv":
        return export_to_csv(data, filepath)
    elif format in ("excel", "xlsx"):
        return export_to_excel(data, filepath)
    else:
        raise ValueError(f"Format '{format}' tidak didukung. Gunakan 'csv' atau 'excel'.")