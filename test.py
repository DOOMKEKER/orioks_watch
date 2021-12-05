from requests import Session
from bs4 import BeautifulSoup as bs
import json
 
with Session() as s:
    site = s.get("https://orioks.miet.ru/user/login")
    bs_content = bs(site.content, "html.parser")
    token = bs_content.find("input", {"name":"_csrf"})["value"]
    login_data = {"LoginForm[login]":"8183866","LoginForm[password]":"delorian22", "_csrf":token}
    s.post("https://orioks.miet.ru/user/login",login_data)
    home_page = s.get("https://orioks.miet.ru/student/student")
    student = bs(home_page.content, "html.parser")

    # here lie JSON object with all scores
    json_string =  student.body.contents[6].contents[3].contents[1].string 
    data = json.loads(json_string)
    # print(json.dumps(data, indent=4, ensure_ascii=False))
    for stud in data["dises"]:
        print(stud["name"])
        for km in stud["segments"][0]["allKms"]:
            print(km["sh"], km["balls"][0]["ball"] if (km["balls"] and km["balls"][0]["ball"]) else 0)

