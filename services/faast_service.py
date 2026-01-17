import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import Config


class FaastService:

    @staticmethod
    def download_faast_csv(cycle_id):
        """
        Abre o FAAST, aguarda download MANUAL do CSV
        Retorna o caminho SOMENTE quando o arquivo estiver
        totalmente disponível no disco.
        """

        # =========================
        # PASTA DE DOWNLOAD
        # =========================
        download_dir = os.path.join(Config.RAW_FOLDER, cycle_id)
        os.makedirs(download_dir, exist_ok=True)

        # =========================
        # CHROME CONFIG
        # =========================
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")

        # Perfil fixo (mantém login)
        chrome_options.add_argument(
            r"user-data-dir=C:\chrome-faast-profile"
        )

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        try:
            print("🌐 Abrindo FAAST...")
            driver.get(Config.FAAST_BASE_URL)

            print("🟡 AÇÃO MANUAL NECESSÁRIA:")
            print("➡️ Selecione a data no FAAST")
            print("➡️ Clique em SEARCH")
            print("➡️ Clique em DOWNLOAD")
            print("➡️ O sistema continuará automaticamente")

            # =========================
            # AGUARDAR DOWNLOAD MANUAL
            # =========================
            print("⏳ Aguardando arquivo FAAST ser baixado...")

            timeout_seconds = 15 * 60  # 15 minutos
            elapsed = 0

            final_file = None

            while elapsed < timeout_seconds:
                time.sleep(1)
                elapsed += 1

                files = os.listdir(download_dir)

                for file in files:
                    # Ignora arquivos temporários
                    if file.endswith(".crdownload"):
                        continue

                    # Detecta o arquivo final
                    if file.startswith(Config.FAAST_DOWNLOAD_FILENAME):
                        final_file = os.path.join(download_dir, file)
                        break

                if final_file and os.path.exists(final_file):
                    print(f"✅ Download detectado: {final_file}")
                    return final_file

            raise Exception("❌ Timeout: arquivo FAAST não foi baixado")

        finally:
            driver.quit()
