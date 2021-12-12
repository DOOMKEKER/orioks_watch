from requests import Session
from bs4 import BeautifulSoup as bs
import json
import re

def request_scores(login, password):
    with Session() as s:
        site = s.get("https://orioks.miet.ru/user/login")
        bs_content = bs(site.content, "html.parser")
        token = bs_content.find("input", {"name":"_csrf"})["value"]
        login_data = {"LoginForm[login]":f"{login}","LoginForm[password]":f"{password}", "_csrf":token}

        r = s.post("https://orioks.miet.ru/user/login",login_data)
        if (r.url != "https://orioks.miet.ru/"):
            raise Exception("incorrect login or password")

        home_page = s.get("https://orioks.miet.ru/student/student")
        page = bs(home_page.content, "html.parser")
        scores = page.find(id="forang")
        data = json.loads(scores.contents[0])
        score_list = {}
        for stud in data["dises"]:
            score_list[stud["name"]] = {}
            for km in stud["segments"][0]["allKms"]:
                score_list[stud["name"]][km["sh"]] = (km["balls"][0]["ball"] 
                                                if (km["balls"] and km["balls"][0]["ball"]) else 0)

        return score_list

def check_login(login, password):
    with Session() as s:
        site = s.get("https://orioks.miet.ru/user/login")
        bs_content = bs(site.content, "html.parser")
        token = bs_content.find("input", {"name":"_csrf"})["value"]
        login_data = {"LoginForm[login]":f"{login}","LoginForm[password]":f"{password}", "_csrf":token}

        r = s.post("https://orioks.miet.ru/user/login",login_data)
        if (r.url != "https://orioks.miet.ru/"):
            return False
        return True

def check_notifications(login, password):
    with Session() as s:
        site = s.get("https://orioks.miet.ru/user/login")
        bs_content = bs(site.content, "html.parser")
        token = bs_content.find("input", {"name":"_csrf"})["value"]
        login_data = {"LoginForm[login]":f"{login}","LoginForm[password]":f"{password}", "_csrf":token}

        r = s.post("https://orioks.miet.ru/user/login",login_data)
        if (r.url != "https://orioks.miet.ru/"):
            raise Exception("Incorrect login or password")

        home_page = s.get("https://orioks.miet.ru/student/student")
        student = bs(home_page.content, "html.parser")
        scripts = student.find_all("script")

        notifications = re.findall("\"https:.{4,10}orioks\.miet\.ru.{5,50}[0-9]\"", str(scripts))

        if notifications == []:
            raise Exception("No notifications")

        lists = []
        for strs in notifications:
            lists.append(strs.replace("\\",""))

        return lists

print(check_notifications("8183866","delorian22"))