import os
import sys
import time
import re
import glob
from pathlib import Path

from tqdm.auto import trange

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chromium.service import ChromiumService


def setup_driver():
    # Instanciamos el servicio con el driver para Chrome
    #service = ChromeService(ChromeDriverManager().install())
    service = ChromeService(executable_path="/usr/bin/chromedriver")

    # Agregamos algunas opciones que llevará el driver
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless")

    # Instanciamos el driver especifico para Chrome y lo retornamos
    return webdriver.Chrome(service=service, options=options)


def request_and_download(driver, url):
    # Hacemos la petición a la URL
    driver.get(url)

    # Obteniendo el nombre del anime
    name_anime = driver.find_element(
        by=By.XPATH,
        value='//div[@class="anime__details__title"]/h3').text

    # Obtenemos el nombre del anime
    year_anime = driver.find_element(
        by=By.XPATH,
        value='//div[@class="anime__details__widget"]//ul/li[7]').text
    year_anime = re.findall("\d{4}", year_anime)[0]

    name_dir = f"./Anime/{name_anime} ({year_anime})/Season 01"
    Path(name_dir).mkdir(parents=True, exist_ok=True)

    # Obtenemos el número de capítulos
    number_episodes = driver.find_element(
        by=By.XPATH,
        value='//div[@class="anime__details__widget"]//ul/li[5]').text
    number_episodes = int(number_episodes.split(":")[-1])

    # Llamamos la función para descargar cada capítulo
    print(f"Descargando el anime {name_anime}:")

    for index in trange(1, number_episodes + 1,
                        desc="Capítulo", leave=None, colour="green", initial=1,
                        bar_format="{desc}: {n_fmt} de {total_fmt} |{bar}|[{elapsed}<{remaining}]"):
        url_episode = f"{url}{index}"

        download_a_video(driver=driver,
                         url=url_episode,
                         name_anime=name_anime,
                         name_dir=name_dir,
                         index=index)


def download_a_video(driver, url, name_anime, name_dir, index):
    # Hacemos la consulta a la página del capítulo
    driver.get(url)

    # Buscamos el elemento "menú de descarga"
    download_video_menu = driver.find_element(
        by=By.XPATH, value='//a[@class="video-download"]')
    download_video_menu.click()

    # Buscamos el botón de descarga
    download_video_boton = driver.find_element(
        by=By.XPATH, value='//a[@id="jkdown"]')
    download_video_boton.click()

    # Realizamos una espera hasta que terminé de descargar el archivo completo
    timeout = 120    # segundos

    for t in trange(timeout, desc="Timeout", ascii=True, colour="green", leave=None):
        # Verificamos si existe ya el archivo mp4 del capítulo
        episode_mp4 = f"{str(index).zfill(2)}.mp4"
        file_episode = glob.glob(f"./*-{episode_mp4}")

        if not file_episode:
            time.sleep(1)
        else:
            # Renombramos el capítulo descargado y lo movemos a su carpeta
            os.rename(file_episode[0], f"{name_dir}/E{episode_mp4}")
            break

    if not file_episode:
        print(
            f"\nERROR: Se sobrepasó el Timeout de espera para descargar el {name_anime} CAPÍTULO: {index}.")


def run():
    driver = setup_driver()
    URLs = sys.argv[1:]

    for url in URLs:
        request_and_download(driver, url)

    driver.close()


if __name__ == "__main__":
    run()
