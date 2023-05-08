import requests
from bs4 import BeautifulSoup
import json
import csv

page_num = 1
import re

pattern_title = r'title="(.*?)"'
url = "https://www.imdb.com/search/title/?genres=action,adventure,fantasy&start={page_num}&title_type=video_game"


def gather_Data(url, page_num=1):
    while True:
        if page_num == 5:
            break
        response = requests.get(url.format(page_num=(page_num - 1) * 50 + 1))
        soup = BeautifulSoup(response.content, "html.parser")

        games = soup.find_all("div", class_="lister-item-content")
        if not games:
            break

        for game in games:
            title_elem = game.find("a")
            title = title_elem.text.strip()
            year = title_elem.find_next_sibling("span").text.strip("() Video Game")

            genre_elem = game.find("span", class_="genre")
            genre = [g.strip() for g in genre_elem.text.split(",")]

            rating_elem = game.find("div", class_="ratings-bar")
            # print("Rating element", rating_elem)
            num_votes = ""
            if rating_elem:
                rating = float(rating_elem.strong.text)
            # extragem numarul de voturi
            num_votes = -1
            if rating_elem:
                text = str(rating_elem.find("div", itemprop="aggregateRating"))
                meta_pos = text.find("<meta")
                text = text[0:meta_pos]
                text = text[text.find(" (") + 2:text.find(" votes")]
                num_votes = 0
                for character in text:
                    if character != ",":
                        num_votes = num_votes * 10 + int(character)

            # print("directorelem ", director_elem)
            #

            # 403 Forbidden

            # game_url = "https://www.imdb.com" + title_elem['href']
            # # Send a GET request to the game page
            # game_response = requests.get(game_url)
            # # Parse the HTML content using BeautifulSoup
            # game_soup = BeautifulSoup(game_response.content, 'html.parser')
            # # Find the div that contains the stars element
            # print(game_soup)
            director = []
            voice_actors = []

            if (str(game).find("Director") != -1):
                director_elem = game.find_all("a", href=lambda href: href and "/name/" in href)
                for elem in director_elem:
                    director.append(elem.text.strip() if director_elem else None)

                stars = "None"

                voice_elem = None

                voice_elem = str(game)
                offset = len("<span class=\"ghost\">|</span>")
                start = voice_elem.find("<span class=\"ghost\">|</span>")
                voice_elem = voice_elem[start + offset:]
                voice_elem = voice_elem[voice_elem.find("<a"):voice_elem.find("\n</p>")]
                if voice_elem:
                    line = voice_elem.find(">")
                    while (line != -1):
                        voice_actors.append(voice_elem[voice_elem.find(">") + 1:voice_elem.find("<", 3)])
                        if voice_elem.find("\n") != -1:
                            voice_elem = voice_elem[voice_elem.find("\n") + 1:]
                        else:
                            break
                        line = voice_elem.find(">")
            else:
                voice_elem = game.find_all("a", href=lambda href: href and "/name/" in href)
                for elem in voice_elem:
                    voice_actors.append(elem.text.strip() if voice_elem else None)

            # if voice_elem:
            #     print("VOICE ELEM",voice_elem)
            #     for actor_elem in voice_elem.find_all("a", href=lambda href: href and "/name/" in href):
            #         actor = actor_elem.text.strip()
            #         character_elem = actor_elem.find_next_sibling("p")
            #         character = character_elem.text.strip() if character_elem else None
            #         voice_actors.append({"actor": actor, "character": character})

            description_elem = game.find_all("p")[1]
            description = description_elem.text.strip() if description_elem else None
            print(f"Title: {title}")
            print(f"Year: {year}")
            print(f"Genre: {genre}")
            print(f"Rating: {rating}")

            print(f"Number of Votes: {num_votes}")

            print(f"Director: {director}")
            print(f"Description: {description}")
            print(f"Voice Actors: {voice_actors}")
            print()
            json_entry = {
                "Title": title,
                "Year": year,
                "Genre": genre,
                "Rating": rating,
                "Number of votes:": num_votes,
                "Director": director,
                "Description": description,
                "Voice Actors": voice_actors,
            }
            json_data = json.dumps(json_entry)
            with open("games.json", "a") as f:
                f.write(json_data)
                f.write(",\n")
            with open('games.csv', 'a', newline='') as f:
                # Create a CSV writer
                writer = csv.writer(f)
                # Loop through the JSON data and write each row to the CSV file

                writer.writerow([title, year,genre,rating,num_votes,director,description,voice_actors])
        page_num += 1


if __name__ == '__main__':
    with open("games.json", "w") as f:
        f.write("[\n")
    with open("games.csv", "w") as f:
        f.write("")
    with open('games.csv', 'a', newline='') as f:
        # Create a CSV writer
        writer = csv.writer(f)

        # Write the header row
        writer.writerow(
            ['Title', 'Year', 'Genre', 'Rating', 'Number of votes', 'Director', 'Description', 'Voice Actors'])

    gather_Data(url)
    with open("games.json", "a") as f:
        f.write("]")
