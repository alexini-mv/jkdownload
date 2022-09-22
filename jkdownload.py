import os
import sys
import time
import re
import glob
from pathlib import Path

from tqdm import trange

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chromium.service import ChromiumService


def setup_driver():
    # Instanciamos el servicio con el driver para Chrome
    #service = ChromeService(ChromeDriverManager().install())
    service = ChromeService(executable_path="./chromedriver")

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
    # strings = url.removeprefix("https://jkanime.net/").split("/")
    # name_anime = strings[0]
    name_anime = driver.find_element(
        by=By.XPATH,
        value='//div[@class="anime__details__title"]/h3').text
    
    # Obtenemos el nombre del anime
    year_anime = driver.find_element(
        by=By.XPATH,
        value='//div[@class="anime__details__widget"]//ul/li[7]').text
    year_anime = re.findall("\d{4}", year_anime)[0]

    name_dir = f"./Anime/{name_anime} ({year_anime})"

    Path(name_dir).mkdir(parents=True, exist_ok=True)

    # Obtenemos el número de capítulos
    number_episodes = driver.find_element(
        by=By.XPATH,
        value='//div[@class="anime__details__widget"]//ul/li[5]').text
    number_episodes = int(number_episodes.split(":")[-1])

    # Llamamos la función para descargar cada capítulo
    print(f"Descargando el anime {name_anime}:")

    for index in trange(1, number_episodes + 1):
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
    timeout = 30    # segundos

    for t in range(timeout):

        file_episode = glob.glob(f"./*-{index.zfill(2)}.mp4")
        if not file_episode:
            time.sleep(1)
        else:
            # Rename
            break



        exists_file = os.path.exists(name_file) or os.path.exists(
            name_file.replace("-", ""))

        if not exists_file:
            time.sleep(1)
        else:
            print(f"Archivo {name_file} descargado. :D\n")
            break

    if not exists_file:
        print(
            "ALERTA: Sobrepasó el límite de tiempo de espera para descargar el archivo.\n")


def exist_file():
    pass


def rename_and_move():
    pass


def run():
    driver = setup_driver()

    URLs = sys.argv[1:]

    for url in URLs:
        request_and_download(driver, url)

    # Cerramos el driver, para finalizar el script
    driver.close()
    print("Se cerró el driver")


if __name__ == "__main__":
    run()
