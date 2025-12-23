# Path: tools/tools.py

import pandas as pd
import pdfplumber
import re
import os

class DataTransformer:
    """
    Handles parsing, cleaning, and normalization of bank statements.
    Output is BI-ready DataFrame.
    """

    CANONICAL_MAP = {
        "date": "transaction_date",
        "txn date": "transaction_date",
        "value date": "value_date",
        "particulars": "remarks",
        "narrative": "remarks",
        "description": "remarks",
        "withdrawal": "debit",
        "dr": "debit",
        "deposit": "credit",
        "cr": "credit",
        "bal": "balance"
    }

    def parse_file(self, file_path: str, file_ext: str) -> pd.DataFrame:
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        elif file_ext in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path)
        elif file_ext == ".pdf":
            df = self._parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")

        return self._clean_dataframe(df)

    def _parse_pdf(self, path: str) -> pd.DataFrame:
        rows = []

        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    rows.extend(table)

        if not rows:
            return pd.DataFrame()

        headers = rows[0]
        data = rows[1:]
        return pd.DataFrame(data, columns=headers)

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [str(c).strip().lower() for c in df.columns]
        df.rename(columns=lambda c: self.CANONICAL_MAP.get(c, c), inplace=True)

        df.dropna(how="all", inplace=True)

        if "transaction_date" in df.columns:
            df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

        for col in ["debit", "credit", "balance"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("Cr", "", regex=False)
                    .str.replace("Dr", "", regex=False)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df = df.dropna(subset=["transaction_date"])
        return df

    def export_csv(self, df: pd.DataFrame, session_id: str) -> str:
        output_dir = os.path.join("uploaded_data", session_id)
        os.makedirs(output_dir, exist_ok=True)

        path = os.path.join(output_dir, "cleaned_data.csv")
        df.to_csv(path, index=False)
        return path
