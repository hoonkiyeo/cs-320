# project: p3
# submitter: yeo9
# partner: none
# hours: 20


import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    #recursive search
    def dfs_search(self, node):
        if node in self.visited:
            return False
        self.visited.add(node)
        curr_node = self.go(node)
        for child in curr_node:
            self.dfs_search(child)

    #non-recursive search
    def bfs_search(self, node):
        todo = [node]  # todo_list (nodes to be visited)
        self.visited.add(node)
        while len(todo) > 0:
            curr_node = todo.pop(0)
            curr_children = self.go(curr_node)
            for child in curr_children:
                if child not in self.visited:
                    todo.append(child)
                    self.visited.add(child)

class FileScraper(GraphScraper):
    def go(self, node):
        if os.path.exists("file_nodes"):
            file_name = node + ".txt"
            file = os.path.join("file_nodes", file_name)
            with open(file, "r") as f:
                lines = list(f)
                children = lines[1].strip().split(" ")
                # append the BFS string (line 3 of the file) to the BFSorder list
                self.BFSorder.append(lines[2].replace("BFS:", "").strip())
                # append the DFS string (line 4 of the file) to the DFSorder list
                self.DFSorder.append(lines[3].replace("DFS:", "").strip())
                return children


# part2
class WebScraper(GraphScraper):
    # required
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver

    # these three can be done as groupwork
    def go(self, url):
        self.driver.get(url)
        links = self.driver.find_elements_by_tag_name("a")
        children = []
        for link in links:
            children.append(link.get_attribute("href"))

        # find bfs and dfs buttons and click them
        bfs_btn = self.driver.find_element_by_id("BFS")
        dfs_btn = self.driver.find_element_by_id("DFS")
        bfs_btn.click()
        dfs_btn.click()

        #append numbers (passwords)
        self.BFSorder.append(bfs_btn.text)
        self.DFSorder.append(dfs_btn.text)

        return children

    def dfs_pass(self, start_url):
        self.visited = set()  # override
        self.DFSorder = []  # override
        self.dfs_search(start_url)

        dfs_pwd = ""
        for letter in self.DFSorder:
            dfs_pwd += str(letter)
        return dfs_pwd

    def bfs_pass(self, start_url):
        self.visited = set()
        self.BFSorder = []
        self.bfs_search(start_url)

        bfs_pwd = ""
        for letter in self.BFSorder:
            bfs_pwd += str(letter)
        return bfs_pwd

    #         pass

    # write the code for this one individually
    def protected_df(self, url, password):
        self.driver.get(url)
        clear = self.driver.find_element_by_id("btnclear")
        clear.click()
        for letter in password:
            keyboard = self.driver.find_element_by_id("btn"+letter)
            keyboard.click()
        go = self.driver.find_element_by_id("attempt-button")
        go.click()
        time.sleep(0.3)
        source_1 = self.driver.page_source
        location_btn = self.driver.find_element_by_id("more-locations-button")
        location_btn.click()
        time.sleep(0.3)
        source_2 = self.driver.page_source

        while source_1 != source_2:
            location_btn = self.driver.find_element_by_id("more-locations-button")
            source_1 = self.driver.page_source
            location_btn.click()
            time.sleep(0.3)
            source_2 = self.driver.page_source
        df = pd.read_html(source_2)
        return df[0]
      