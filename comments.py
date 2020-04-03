# -*- coding: utf-8 -*-
import argparse
import json
import os
import requests
from bs4 import BeautifulSoup

COMMENTS_URL = "https://scratch.mit.edu/site-api/comments/project/{0}/?page={1}"

def get_arguments():
    parser = argparse.ArgumentParser(description="Download Scratch projects.")

    # Arguments related to input
    inputs = parser.add_mutually_exclusive_group(required=True)
    #inputs.add_argument("-s", dest="studio", nargs="*", help="Studio ID. Will scrape all projects from the studio with the given ID.")
    inputs.add_argument("-p", dest="project", nargs="*", help="Project ID. Will scrape one project for each ID provided.")
    # Arguments related to output
    parser.add_argument("-d", dest="output_directory", help="Output directory. Will save output to this directory, and create the directory if doesn’t exist.")
    parser.add_argument("-n", dest="output_name", help="Name of the output JSON file, if only a single output file is desired. Otherwise, will save projects to individual JSON files.")

    return parser.parse_args()

def get_project_ids(arguments):
    """Given input arguments, return a set of all the project IDs."""
    projects = list()
    if arguments.project is not None:
        projects = arguments.project
    # elif arguments.studio is not None:
    #     for s in arguments.studio:
    #         projects += get_projects_in_studio(helpers.get_id(s))
    # elif arguments.project_list is not None:
    #     for p in arguments.project_list:
    #         projects += get_ids_from_file(p)
    # elif arguments.studio_list is not None:
    #     for s in arguments.studio_list:
    #         studios = get_ids_from_file(s)
    #         for studio in studios:
    #             projects += get_projects_in_studio(studio)

    return set(projects)

# Iterates through each page of comments, calling `download_comments` for each separate API call
def download_page(id_set, output_directory=os.getcwd(), file_name=None):
    page = 1
    master_comments = []
    master_users = []
    master_count = 0

    while True:
        try: 
            comment_list, comment_count = download_comments(id_set, page)
            user_list = download_users(id_set, page)
            master_comments.extend(comment_list)
            master_users.extend(user_list)
            master_count += comment_count
            page += 1
        except:
            break
    return (master_comments, master_users, master_count)

# Downloads comments for the given project ID and page number
def download_comments(id_set, page, output_directory=os.getcwd(), file_name=None):
    comments = []
    comment_count = 0
    for id in id_set:
        url = COMMENTS_URL.format(id, page)
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError("GET {0} failed with status code {1}".format(r.status_code, url))
    # Use Beautiful Soup to scrape the webpage for the comments that we want
    soup = BeautifulSoup(r.content, 'html.parser')
    #print(soup)
    all_comments = soup.select(".content")
    # Go through each comment and clean, adding comment to comments list
    for comment in all_comments:
        clean_comment = comment.get_text().strip()
        if clean_comment != '[deleted]':
            comments.append(clean_comment)
            comment_count += 1
    return (comments, comment_count)

# Returns a list of the usernames that commented on the project
def download_users(id_set, page, output_directory=os.getcwd(), file_name=None):
    users = []
    for id in id_set:
        url = COMMENTS_URL.format(id, page)
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError("GET {0} failed with status code {1}".format(r.status_code, url))
    # Use Beautiful Soup to scrape the webpage for the comments that we want
    soup = BeautifulSoup(r.content, 'html.parser')
    # Go through each user, adding user to users list
    all_users = soup.select(".name")
    for user in all_users:
        clean_user = user.get_text().strip()
        users.append(clean_user)
    return users

def main():
    arguments = get_arguments()
    projects = get_project_ids(arguments)

    if arguments.output_directory is None:
        download_page(projects, file_name=arguments.output_name)
    else:
        download_page(projects, output_directory=arguments.output_directory, file_name=arguments.output_name)

if __name__ == "__main__":
    main()