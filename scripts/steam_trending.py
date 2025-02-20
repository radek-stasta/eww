import os
import html
import requests
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def download_image(url, output_dir, index):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(output_dir, f"{index}.jpg")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    return None

try:
    # Create folder for output files if not exists
    outputPath = os.path.expanduser('~') + '/.local/share/eww-output'
    imageOutputPath = os.path.expanduser('~') + '/.local/share/eww-output/trending'

    pathExist = os.path.exists(outputPath)
    if not pathExist:
        os.makedirs(outputPath)

    # Delete imageOutputPath folder if it exists
    if os.path.exists(imageOutputPath):
        shutil.rmtree(imageOutputPath)

    os.makedirs(imageOutputPath)

    # TRENDING
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options = options)
    driver.get("https://steamdb.info/")
    bs = BeautifulSoup(driver.page_source, "html.parser")

    productsContainer = bs.find("div", {"class": "container-products"})
    productsRows = productsContainer.find_all("div", {"class": "row"})

    firstRowTables = productsRows[0].find_all("table", {"class": "table-products"})
    tableTrending = firstRowTables[1]
    appRows = tableTrending.find_all("tr", {"class": "app"})

    trending = []

    # Create objects
    for app in appRows:
        columns = app.find_all("td")

        # Get image src from app
        appId = app.get("data-appid")
        imgSrc = "https://steamcdn-a.akamaihd.net/steam/apps/%s/header.jpg" % (appId)

        name = columns[2].find("a", {"class": "css-truncate"}).get_text(strip=True)

        try:
            players = columns[4].get_text()
        except:
            players = "0"

        # Download the image and get the local file path
        local_image_path = download_image(imgSrc, imageOutputPath, len(trending))
        if local_image_path:
            gameInfo = {"name": html.escape(name), "players": players, "imgSrc": local_image_path, "appId": appId}
            trending.append(gameInfo)

    # Sort by players
    trending = sorted(trending, key=lambda x: int(x['players'].replace(',', '')), reverse=True)

    now = datetime.now()

    # Create eww file contents
    output = """
    (box
      :orientation 'v'
      :spacing 4
      :space-evenly false
      (label
        :style 'color: #a3be8c; font-weight: bold; margin-bottom: 8px'
        :markup 'TRENDING GAMES (%s)'
      )
    """ % (now.strftime("%d.%m.%Y %H:%M:%S"))

    # Take two games and print them (because of two images side by side for better display)
    printedGames = []
    for gameInfo in trending:
        printedGames.append(gameInfo)
        if len(printedGames) == 2:
            output += """
            (box
              :orientation 'h'
              :space-evenly false
              :spacing 8
              (box
                :width 140
                :height 65
                (image
                  :path '%s'
                  :image-width 140
                  :image-height 65
                )
              )
              (box
                :width 140
                :height 65
                (image
                  :path '%s'
                  :image-width 140
                  :image-height 65
                )
              )
              (box
                :orientation 'v'
                (box
                  :orientation 'h'
                  :space-evenly false
                  (button
                    :width 400
                    :onclick "google-chrome-stable https://store.steampowered.com/app/%s"
                    (label
                      :truncate true
                      :markup '%s'
                    )
                  )
                  (label
                    :width 100
                    :markup '%s'
                  )
                )
                (box
                  :orientation 'h'
                  :space-evenly false
                  (button
                    :width 400
                    :onclick "google-chrome-stable https://store.steampowered.com/app/%s"
                    (label
                      :truncate true
                      :markup '%s'
                    )
                  )
                  (label
                    :width 100
                    :markup '%s'
                  )
                )
              )
            )
            """ % (printedGames[0]["imgSrc"], printedGames[1]["imgSrc"], printedGames[0]["appId"], printedGames[0]["name"], printedGames[0]["players"], printedGames[1]["appId"], printedGames[1]["name"], printedGames[1]["players"])

            printedGames = []

    # Print last game if printedGames are not empty
    if len(printedGames) == 1:
        output += """
            (box
              :orientation 'h'
              :space-evenly false
              :spacing 8
              (box
                :width 140
                :height 65
                (image
                  :path '%s'
                  :image-width 140
                  :image-height 65
                )
              )
              (box
                :width 140
                :height 65
              )
              (box
                :orientation 'v'
                :space-evenly false
                (box
                  :orientation 'h'
                  :space-evenly false
                  (button
                    :width 400
                    :onclick "google-chrome-stable https://store.steampowered.com/app/%s"
                    (label
                      :truncate true
                      :markup '%s'
                    )
                  )
                  (label
                    :width 100
                    :markup '%s'
                  )
                )
              )
            )
            """ % (printedGames[0]["imgSrc"], printedGames[0]["appId"], printedGames[0]["name"], printedGames[0]["players"])

    output += ')'

    outputFile = open(os.path.expanduser('~') + '/.local/share/eww-output/steam_trending.yuck', 'w+')
    outputFile.write(str(output))
    outputFile.close()
finally:
    try:
        driver.quit()
    except:
        pass