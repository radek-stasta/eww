import os
import html
import requests
import shutil
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def convert_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d %b')
        return date_obj.strftime('%-d.%-m.')
    except ValueError:
        date_obj = datetime.strptime(date_str, '%b %Y')
        return date_obj.strftime('%b %Y')

def download_image(url, output_dir, index):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(output_dir, f"{index}.jpg")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    return None

def group_games_by_date(games):
    releases = {}
    month_year_releases = {}

    for game in games:
        date = game["date"]
        try:
            datetime.strptime(date, '%d %b')
            if date not in releases:
                releases[date] = []
            releases[date].append(game)
        except ValueError:
            if date not in month_year_releases:
                month_year_releases[date] = []
            month_year_releases[date].append(game)

    # Sorting games by followers in each release date
    for date in releases:
        releases[date] = sorted(releases[date], key=lambda x: int(x["followers"].replace(',', '')), reverse=True)

    for date in month_year_releases:
        month_year_releases[date] = sorted(month_year_releases[date], key=lambda x: int(x["followers"].replace(',', '')), reverse=True)

    sorted_releases = [{"date": convert_date(date), "games": games} for date, games in releases.items()]
    sorted_month_year_releases = [{"date": date, "games": games} for date, games in month_year_releases.items()]

    return sorted_releases + sorted_month_year_releases

try:
    # Create folder for output files if not exists
    outputPath = os.path.expanduser('~') + '/.local/share/eww-output'
    imageOutputPath = os.path.expanduser('~') + '/.local/share/eww-output/upcoming'

    pathExist = os.path.exists(outputPath)
    if not pathExist:
        os.makedirs(outputPath)

    # Delete imageOutputPath folder if it exists
    if os.path.exists(imageOutputPath):
        shutil.rmtree(imageOutputPath)

    os.makedirs(imageOutputPath)

    # Calculate current year, current date, and date 14 days from now
    current_year = datetime.now().year
    current_date = datetime.now().strftime("%Y-%m-%d")
    max_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    # Construct the URL
    url = f"https://steamdb.info/stats/gameratings/{current_year}/?min_followers=1000&max_followers=&min_release={current_date}&max_release={max_date}&sort=release_asc"

    # UPCOMING
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options = options)
    driver.get(url)
    bs = BeautifulSoup(driver.page_source, "html.parser")

    releasesContainer = bs.find("table", {"class": "table-sales"})

    totalGames = 0
    games = []
    appRows = releasesContainer.find_all("tr", {"class": "app"})

    for app in appRows:
        gameInfo = {}

        # Get image src from app
        appId = app.get("data-appid")
        imgSrc = "https://steamcdn-a.akamaihd.net/steam/apps/%s/header.jpg" % (appId)

        nameTd = app.find_all('td')[2]
        name = nameTd.find('a', {"class": "b"}).get_text(strip=True)
        date = app.find_all('td')[6].get_text(strip=True)
        followers = app.find_all('td')[7].get_text(strip=True)

        # Download the image and get the local file path
        local_image_path = download_image(imgSrc, imageOutputPath, totalGames)
        if local_image_path:
            gameInfo = {"name": html.escape(name), "followers": followers, "imgSrc": local_image_path, "appId": appId, "date": date}
            games.append(gameInfo)

        totalGames = totalGames + 1

    # Group games by release date
    releases = group_games_by_date(games)

    now = datetime.now()

    # Create eww file contents
    output = """
    (box
      :orientation 'v'
      :spacing 4
      :space-evenly false
      (label
        :style 'color: #a3be8c; font-weight: bold; margin-bottom: 8px'
        :markup 'UPCOMING RELEASES (%s)'
      )
    """ % (now.strftime("%d.%m.%Y %H:%M:%S"))

    # Take two games and print them (because of two images side by side for better display)
    printedGames = []
    for releaseDay in releases:
        if not releaseDay['games']:
            continue  # if games array is empty, skip to the next iteration

        output += """
        (label
          :style 'color: #bf616a; margin-top: 4px; margin-bottom: 4px'
          :markup '%s'
        )
        """ % (releaseDay['date'])

        for gameRelease in releaseDay['games']:

            printedGames.append(gameRelease)
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
                """ % (printedGames[0]["imgSrc"], printedGames[1]["imgSrc"], printedGames[0]["appId"], printedGames[0]["name"], printedGames[0]["followers"], printedGames[1]["appId"], printedGames[1]["name"], printedGames[1]["followers"])

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
                """ % (printedGames[0]["imgSrc"], printedGames[0]["appId"], printedGames[0]["name"], printedGames[0]["followers"])

            printedGames = []

    output += ')'

    outputFile = open(os.path.expanduser('~') + '/.local/share/eww-output/steam_upcoming.yuck', 'w+')
    outputFile.write(str(output))
    outputFile.close()
finally:
    try:
        driver.quit()
    except:
        pass