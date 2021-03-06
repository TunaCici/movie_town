"""
Author: Tuna Cici
Written on: 23/08/2021

What is this:
This utilty provides simple interface
to imdb files such as, movies, actors.
"""

import json
import uuid
import os
import requests
import pandas as pd
from io import FileIO
from numpy import int64

if __name__ == "utils." + os.path.basename(__file__)[:-3]:
    # importing from outside the package
    from utils import config
    from utils import logger
else:
    # importing from main and inside the package
    import config
    import logger


FILE_MOVIES: FileIO
FILE_RATINGS: FileIO
FILE_TITLE_PRINCIPALS: FileIO
IMDB_LOGGER = logger.CustomLogger()

TMDB_API_SESSION = requests.session()
TMDB_IMG_SESSION = requests.session()

def open_files():
    global FILE_MOVIES
    global FILE_RATINGS
    global FILE_TITLE_PRINCIPALS

    IMDB_LOGGER.log_info("Opening files...")
    FILE_MOVIES = open(config.PROJECT_DIR + "data/imdb_movies.csv", encoding="utf8")
    FILE_RATINGS = open(config.PROJECT_DIR + "data/imdb_ratings.csv", encoding="utf8")
    FILE_TITLE_PRINCIPALS = open(config.PROJECT_DIR + "data/imdb_title_principals.csv", encoding="utf8")
    IMDB_LOGGER.log_info("Files opened.")

def close_files():
    global FILE_MOVIES
    global FILE_RATINGS
    global FILE_TITLE_PRINCIPALS

    IMDB_LOGGER.log_info("Closing files...")
    FILE_MOVIES.close()
    FILE_RATINGS.close()
    FILE_TITLE_PRINCIPALS.close()
    IMDB_LOGGER.log_info("Files closed.")

def print_all(file: str):
    """
    Options: movies, ratings, principals
    """
    pd_file = pd.read_csv(file, low_memory=False)
    df = pd.DataFrame(pd_file)
    print(df)

def get_with_index(file: FileIO, index : int) -> dict:
    """
    Get's the data stated by the index from the file.
    Returns it as dict.
    """

    if index < 0:
        IMDB_LOGGER.log_warning("Index must be greater than 0.")
        return
    
    # dataframe
    df = pd.read_csv(file, low_memory=False)

    # list of columns
    cl = df.columns

    return_value = {}

    # get the data from file to a dict
    for i in cl:
        if type(df[i][index]) is int64:
            return_value[i] = int(df[i][index])
        else:
            return_value[i] = df[i][index]
       
    return return_value

def get_columns(file: FileIO) -> list:
    """
    Returns all the columns in a file as a list.
    """
    df = pd.read_csv(file, low_memory=False)
    return df.columns

def get_image(imdb_id: str) -> bytes:
    api_key = "fe0c11c0aeee82176ba4b9f31e43b286"
    url = "https://api.themoviedb.org/3/find/" + imdb_id +"?api_key=" + api_key + "&external_source=imdb_id"

    response = TMDB_API_SESSION.get(url)
    if response.status_code == 200:
        results = response.json()["movie_results"]

        # no movie was found
        if len(results) == 0:
            print(f"could not found the movie: {imdb_id}")
            return None

        path = results[0]["poster_path"]
        # no poster was found
        if path is None:
            print(f"no poster found.")
            return None
        
        img_data = TMDB_IMG_SESSION.get("https://image.tmdb.org/t/p/original" + path).content
        return img_data
    else:
        print("an error occured.")
        return None

def print_all(file: FileIO):
    pd_file = pd.read_csv(FILE_MOVIES, low_memory=False)
    df = pd.DataFrame(pd_file)

    print(df)


def init_movie_images():
    pd_file = pd.read_csv(FILE_MOVIES, low_memory=False)
    df = pd.DataFrame(pd_file)

    # list all images in data/posters folder
    curr_posters = os.listdir(config.PROJECT_DIR + "data/posters")

    total_found = 0
    
    for imdb_id in df["imdb_title_id"]:
        print(f"total_found: {total_found}")
        print(f"looking for: {imdb_id}")
        file_name = imdb_id + ".jpg"
        if file_name in curr_posters:
            print("Poster already exists.")
            total_found += 1
        else:
            img_data = get_image(str(imdb_id))
            if img_data is not None:
                with open(config.PROJECT_DIR + "data/posters/" + imdb_id + ".jpg", "wb") as f:
                    f.write(img_data)
                print(f"Save {file_name}")
                total_found += 1

def drop_column(file: FileIO, columns: list):
    pd_file = pd.read_csv(file, low_memory=False)
    df = pd.DataFrame(pd_file)
    df.drop(columns, axis=1, inplace=True)
    df.to_csv("imdb_movies.csv", encoding="utf8")

def list_high_rated(file: FileIO):
    pd_file = pd.read_csv(FILE_MOVIES, low_memory=False)
    df = pd.DataFrame(pd_file)
    
    total = 0
    for idx, i in df.iterrows():
        if 7.5 <= i["avg_vote"]:
            title = i["title"]
            score = i["avg_vote"]
            total += 1
            print(f"{title} with score of {score}")

    print(f"Total of: {total}")

def update_path_of_titles(file: FileIO):
    pd_file = pd.read_csv(file, low_memory=False)
    df = pd.DataFrame(pd_file)

    for idx, i in df.iterrows():
        if os.path.isfile(config.PROJECT_DIR + "data/posters/" + i["imdb_title_id"] + ".jpg"):
            df.at[idx, "poster_path"] = "data/posters/" + i["imdb_title_id"] + ".jpg"
        
    print(df)
    df.to_csv("imdb_movies.csv")

def update_id_of_titles(file: FileIO):
    pd_file = pd.read_csv(file, low_memory=False)
    df = pd.DataFrame(pd_file)

    for idx, i in df.iterrows():
        b_unique_id = uuid.uuid4()
        str_unique_id = str(b_unique_id)
        df.at[idx, "id"] = str_unique_id

    print(df)
    df.to_csv("updated_movies.csv")

if __name__ == "__main__":
    IMDB_LOGGER.log_info("Started main function.")
    open_files()
    hey = get_with_index(FILE_MOVIES, 56)
    close_files()

    open_files()
    # TODO: Write your code here for data manipulation
    init_movie_images()
    #list_high_rated(FILE_MOVIES)
    #add_path_to_titles(FILE_MOVIES)
    #update_path_of_titles(FILE_MOVIES)
    #update_id_of_titles(FILE_MOVIES)
    #print_all(FILE_MOVIES)
    #close_files()