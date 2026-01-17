import os
import pandas as pd
from config import Config


class ProcessingService:

    @staticmethod
    def process_faast_csv(raw_csv_path, cycle_id):

        print("📊 Processando FAAST CSV")
        print(f"📄 Arquivo: {raw_csv_path}")

        df = pd.read_csv(raw_csv_path)
        print(f"📈 Linhas totais: {len(df)}")

        # =========================
        # COLUNAS FAAST (FIXAS)
        # =========================
        USER_COL = 1      # B
        SKU_COL = 2       # C
        ADDRESS_COL = 9   # J

        if df.shape[1] <= ADDRESS_COL:
            raise Exception(
                "CSV inválido: colunas insuficientes (esperado até J)"
            )

        data = pd.DataFrame({
            "user": df.iloc[:, USER_COL],
            "sku": df.iloc[:, SKU_COL],
            "address": df.iloc[:, ADDRESS_COL]
        })

        # =========================
        # LIMPEZA
        # =========================
        data = data.dropna(subset=["user", "address"])
        data["user"] = data["user"].astype(str).str.strip()
        data["sku"] = data["sku"].astype(str).str.strip()
        data["address"] = data["address"].astype(str).str.strip()

        if data.empty:
            print("⚠️ CSV sem dados válidos")
            return []

        # =========================
        # SAÍDA
        # =========================
        output_dir = os.path.join(
            Config.PROCESSED_FOLDER,
            cycle_id
        )
        os.makedirs(output_dir, exist_ok=True)

        results = []

        # =========================
        # AGRUPAR POR USER
        # =========================
        for user, group in data.groupby("user"):

            addresses = group["address"].unique()
            skus = group["sku"].unique()

            if len(addresses) == 0:
                continue

            file_name = f"{user}.csv"
            local_path = os.path.join(output_dir, file_name)

            pd.DataFrame({
                "ScannableId": addresses
            }).to_csv(local_path, index=False)

            print(
                f"✅ {file_name} | "
                f"Endereços: {len(addresses)} | "
                f"SKUs: {len(skus)}"
            )

            results.append({
                "aaLogin": user,
                "fileName": file_name,
                "localPath": local_path,
                "totalAddresses": len(addresses),
                "totalSkus": len(skus)
            })

        print(f"🏁 Processamento concluído: {len(results)} arquivos")

        return results
