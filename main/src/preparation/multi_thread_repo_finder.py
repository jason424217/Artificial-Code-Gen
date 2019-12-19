# https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Producer_Consumer_using_Queue.php
# Above link used a reference for threading code

import threading
from queue import Queue
import requests
from requests.exceptions import ConnectionError
import time
import os
import re
import argparse
from pymongo import MongoClient

MAX_QUEUE_SIZE = 0
repos_to_download = None
api_keys = Queue()
language_count_lock = threading.Lock()

API_URL = "http://api.github.com"
LANGUAGE_SET = set(["C++", "Python", "Scala", "JavaScript", "Java"])
TRANSLATE_EXTENSIONS = {"cpp": "C++", "py": "Python", "scala": "Scala", "js": "JavaScript", "java": "Java"}
LANGUAGE_COUNT = {"cpp": 0, "py": 0, "scala": 0, "js": 0, "java": 0}
LANGUAGE_MAX = 1000000

CLIENT = None
SORT = None

VERBOSE = True
DATA_PATH = None

class APIKey():
    def __init__(self, TOKEN_STRING):
        self.TOKEN = TOKEN_STRING
        self.calls_left = 5000
        self.api_reset_time = None  # This is currently an unused field


# This class is simply responsible for pulling down as many repositories from the
# github API as it can. It is the PRODUCER of tasks
class RepoFinder(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, key=None, url=None):
        super(RepoFinder, self).__init__()
        self.target = target
        self.name = name
        self.token = key.TOKEN
        self.start_url = url

    def run(self):

        if self.start_url:
            url = self.start_url
        else:
            url = API_URL + "/repositories?"

        headers = {'Authorization': 'token %s' % self.token}  # Add auth token to request header
        check_remaining_calls(headers)
        r = requests.get(url=url, headers=headers)  # Make get request

        for repo in r.json():
            repos_to_download.put((repo["full_name"], repo["contents_url"], repo["languages_url"]), block=True,
                                  timeout=None)

        while 'next' in r.links.keys():  # while there is a "next" page of results

            url = r.links['next']['url']
            if VERBOSE: print(self.name + " getting repos from: " + str(url))

            check_remaining_calls(headers)
            r = requests.get(url=url, headers=headers)

            with open("repos/Next_repo_page_to_see.txt", "a+") as next_repo:
                try:
                    next_repo.write(r.links['next']['url'])
                    next_repo.write("\n")
                except ValueError:
                    pass

            for repo in r.json():
                repos_to_download.put((repo["full_name"], repo["contents_url"], repo["languages_url"]), block=True,
                                      timeout=None)

            # Check if all languages are done, if so, kill this thread.
            if len(LANGUAGE_SET) == 0:
                if VERBOSE: print("All languages complete, producer is dying, goodbye")
                return

        return


# This class is responsible for grabbing a repository reference from the queue and downloading and sorting it.
# It is a CONSUMER of tasks
class RepoConsumer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(RepoConsumer, self).__init__()
        self.target = target
        self.name = name

    def run(self):
        while True:
            if not repos_to_download.empty():
                # grab repo from the queue
                repo = repos_to_download.get(block=True, timeout=None)
                key = api_keys.get()
                language_found = self.contains_relevant_languages(repo, key)

                if not language_found:
                    api_keys.put(key)
                    api_keys.task_done()
                    repos_to_download.task_done()
                    continue

                if VERBOSE: print(self.name + " getting files from: " + repo[0])

                self.get_files_from_repo(repo, key)
                api_keys.put(key)
                api_keys.task_done()
                repos_to_download.task_done()

                # This kills the consumers once all languages have been found
                if len(LANGUAGE_SET) == 0:
                    if VERBOSE: print(self.name + " is dying, goodbye")
                    return
            else:
                if len(LANGUAGE_SET) == 0:
                    if VERBOSE: print(self.name + " is dying, goodbye")
                    return
        return

    @staticmethod
    def contains_relevant_languages(repo, key):

        headers = {'Authorization': 'token %s' % key.TOKEN}  # Add auth token to request header
        check_remaining_calls(headers)

        languages_url = repo[2]
        lang_request = requests.get(url=languages_url, headers=headers)

        languages_in_repo = set(lang_request.json().keys())
        if LANGUAGE_SET & languages_in_repo:
            return True

        return False

    def get_files_from_repo(self, repo, key):

        headers = {'Authorization': 'token %s' % key.TOKEN}  # Add auth token to request header
        full_repo_name = repo[0].split("/")
        full_repo_name = full_repo_name[0] + "_" + full_repo_name[1]

        self.recursive_find_files_in_dir(full_repo_name, repo[1], headers)
        pass

    def recursive_find_files_in_dir(self, full_repo_name, url, headers):

        check_remaining_calls(headers)

        url = re.sub("\{\+path\}", "", url)  # If there is a {+path} on the end of the contents url, remove it
        url = re.sub("\?.*", "", url)  # If there are query strings at the end of the url, remove them all
        r = requests.get(url=url, headers=headers)

        response_jsons = r.json()

        if isinstance(response_jsons, list):
            for item in response_jsons:
                try:
                    if item["type"] == "file":
                        extension = item["name"].split(".")[-1]
                        if extension in TRANSLATE_EXTENSIONS.keys():

                            # If SORT (whichever one we're using) returns True, keep sorting.
                            # Otherwise, this is a bad repo (maybe its a duplicate) and we should no longer find files

                            if SORT(item, extension, full_repo_name, headers):
                                continue
                            else:
                                if VERBOSE: print("No longer collecting from repo " + str(full_repo_name))
                                return

                    elif item["type"] == "dir":
                        self.recursive_find_files_in_dir(full_repo_name, item["url"], headers)
                except ValueError:
                    print("Item not of recognized type")
        else:
            # Test for this functionality, github.com/pierrevalade/trackit , an empty repo      
            print(self.name + ": Repository is likely empty")
            print(response_jsons)
            return

    @staticmethod
    def sort_into_folder(item, extension, full_repo_name, headers):

        # TODO: this is not an ideal solution; it would be better to continually check where the langugaes in the repo
        # are still in the LANGUAGE_SET
        if TRANSLATE_EXTENSIONS[extension] not in LANGUAGE_SET:
            return

        full_relative_path = DATA_PATH + "/" + extension + "/" + full_repo_name + "/"
        if not os.path.exists(full_relative_path):
            os.makedirs(full_relative_path)

        file_name = re.sub("/", "_", item["path"])  # We will name each file with it's path + filename

        url = item["download_url"]
        if url:
            check_remaining_calls(headers) # possible unnecessary, because the next request is not an api call
            r = requests.get(url=url, headers="")  # Retrieves the raw file data from github (Not an API request)

            with open(os.path.join(full_relative_path, file_name), 'w') as file:
                file.write(r.text)

            # If we hit one million files, it will remove that language from the set of languages we want to download
            language_count_lock.acquire()
            LANGUAGE_COUNT[extension] += 1
            if LANGUAGE_COUNT[extension] > LANGUAGE_MAX:
                LANGUAGE_SET.discard(TRANSLATE_EXTENSIONS[extension])
                if VERBOSE: print("Language " + TRANSLATE_EXTENSIONS[extension] + " has been discarded from the set: " + str(LANGUAGE_SET))
            language_count_lock.release()

            return True

        return False

    @staticmethod
    def sort_into_collection(item, extension, full_repo_name, headers):

        # TODO: this is not an ideal solution; it would be better to continually check where the langugaes in the repo
        # are still in the LANGUAGE_SET
        if TRANSLATE_EXTENSIONS[extension] not in LANGUAGE_SET:
            return

        url = item["download_url"]

        if url:
            check_remaining_calls(headers) # possible unnecessary, because the next request is not an api call
            r = requests.get(url=url, headers="")  # Retrieves the raw file data from github (Not an API request)

            db = CLIENT.file_level
            collection = db[extension]
            record = {"repo_name": full_repo_name, "path_in_repo": item["path"], "url": url,
                      "file_name": item["path"].split("/")[-1], "file_contents": r.text, "partition": None}

            # This is an optimization not present in the file sorting: if this file is already in the database
            # it won't re-add it. Checking whether a file is already in the dataset is impractical when saving to disk,
            # but easy here. Unique-ness is qualified by download url.
            check_if_in_collection = {"url": url}
            in_collection = collection.count_documents(check_if_in_collection)

            if in_collection == 0:
                collection.insert_one(record)
            else:
                if VERBOSE: print("Duplicate file found from " + str(url) + ", ending sort of this repo")
                return False

            # If we hit one million files, it will remove that language from the set of languages we want to download
            language_count_lock.acquire()
            LANGUAGE_COUNT[extension] += 1
            if LANGUAGE_COUNT[extension] > LANGUAGE_MAX:
                LANGUAGE_SET.discard(TRANSLATE_EXTENSIONS[extension])
                if VERBOSE: print("Language " + TRANSLATE_EXTENSIONS[extension] + " has been discarded from the set: " + str(LANGUAGE_SET))
            language_count_lock.release()

            return True


def check_remaining_calls(headers):
    rate_limit_url = API_URL + "/rate_limit"

    try:
        rate_request = requests.get(url=rate_limit_url, headers=headers)  # Make get request
    except ConnectionError:
        if VERBOSE: print("Caught ConnectionError, continuing.")
        return

    try:
        if int(rate_request.json()["resources"]["core"]["remaining"]) < 1:
            if VERBOSE: print("Thread is over the API limit, sleeping")
            time_of_reset = float(rate_request.json()["resources"]["core"]["reset"])  # this is in utc epoch seconds
            current_time = time.time()  # this also returns in utc epoch seconds (if on unix system)
            time_to_wait = time_of_reset - current_time  # can just be subtracted: they're seconds, not dt objects.

            time.sleep(time_to_wait)

    except KeyError:
        print(rate_request.json())
        print("Caught KeyError when checking remaining calls, continuing")


def populate_api_keys_queue(path):
    with open(os.path.abspath(path), 'r') as file:
        count = 0
        for line in file:
            count += 1
            api_keys.put(APIKey(line.strip()))
    return count


def parse_arguments():
    parser = argparse.ArgumentParser(description="multi_thread_repo_finder.py : Uses GitHub API Tokens to find and "
                                                 "download publicly available github repositories\n")
    parser.add_argument("-s", "--start_url", default=None, help="Optional. Changes first page of API results,"
                                                                " for example: "
                                                                "\"https://api.github.com/repositories?since=23400\", "
                                                                "default behavior starts the download at the "
                                                                "first page")

    parser.add_argument("-m", "--mongo", action="store_true", help="If enabled data is stored to database instead of "
                                                                   "disk")

    parser.add_argument("-v", "--verbose", action="store_true", help="Optional. If enabled program prints full "
                                                                     "threading information during run")
    parser.add_argument("-q", "--queue_size", default=500, help="Optional. Argument changes queue size, default size "
                                                                "is 500, must be int")
    parser.add_argument("-p", "--personal_tokens", default="personal_tokens.txt", help="Path to file which contains "
                                                                                       "one GitHub Personal Token with "
                                                                                       "public repo access per line.")
    parser.add_argument("-d", "--data_path", default="../../data/raw", help="Where raw data should be stored on the "
                                                                            "machine")

    parser.add_argument("-dh", "--db_host", default="localhost", help="The location of the mongo database. If a host"
                                                                      "is provided it overrides storage on disk. Must"
                                                                      "be used with -m flag")

    parser.add_argument("-dp", "--db_port", default=27017, help="The port of the mongo database. Must be used with the"
                                                                "-m flag")

    args = parser.parse_args()

    return args


def main():
    global MAX_QUEUE_SIZE, VERBOSE, DATA_PATH, repos_to_download, CLIENT, SORT
    args = parse_arguments()

    VERBOSE = args.verbose
    MAX_QUEUE_SIZE = int(args.queue_size)
    DATA_PATH = args.data_path

    if args.mongo:
        print("Using mongo")
        CLIENT = MongoClient('localhost', 27017)
        SORT = RepoConsumer.sort_into_collection

    else:
        CLIENT = None
        SORT = RepoConsumer.sort_into_folder

    print("Queue size is " + str(MAX_QUEUE_SIZE))
    repos_to_download = Queue(MAX_QUEUE_SIZE)

    num_tokens = populate_api_keys_queue(args.personal_tokens)  # default is "personal_tokens.txt"

    with open("repos/Next_repo_page_to_see.txt", "a+") as next_repo:
        next_repo.write("\nNEW RUN\n")

    producer_key = api_keys.get()
    producer = RepoFinder(name="producer", key=producer_key, url=args.start_url)
    producer.start()

    for i in range(num_tokens - 1):
        consumer = RepoConsumer(name="CONSUMER_THREAD_" + str(i))
        consumer.start()

    repos_to_download.join()


main()
