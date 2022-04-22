
from audioop import avg
import os
from typing import Dict, List
from requests import request

from fastapi import FastAPI


from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv("../.env")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
NOTION_KEY = os.getenv("NOTION_KEY")
TAG_CLASS_ID = "Tags"
app = FastAPI()

origins = [
    str(os.getenv("FRONT_URL"))
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def save_page_metainfo_json():

    # make request with bearer notion key,
    # and save the json response to notion_info.json

    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}"
    headers = {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-02-22",
    }


    response = request("GET", url, headers=headers)

    print(response.status_code)
    print(response.text)

    

    with open("env_metainfo.json", "w") as f:
        f.write(response.text)
    

def cache_allpage_info_json():

    # make request with bearer notion key,
    # and save the json response to notion_info.json

    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-02-22",
    }


    response = request("POST", url, headers=headers)

    print(response.status_code)
    print(response.text)

    with open("env_pages_info.json", "w") as f:
        f.write(response.text)

import colorsys
import json

def randomcolorfromint(i, N):
    import random
    import colorsys
    h = i / N
    rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    return '#%02x%02x%02x' % (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))


def colorcodetorgb(_color:str)->List[int]:
            return [int(_color[i:i+2], 16) for i in (0, 2 ,4)]


# average input colors
def avg_color(colorlist : List[str])-> str:
    rgb_list = [colorcodetorgb(_color[1:]) for _color in colorlist]
    r, g, b = [sum(x) / len(colorlist) for x in zip(*rgb_list)]
    return '#%02x%02x%02x' % (int(r ), int(g ), int(b ))
    


def generate_graphinfo():
    
    # create tags map
    metainfo = json.load(open("env_metainfo.json"))
    pages_info = json.load(open("env_pages_info.json"))["results"]


    tagset = metainfo["properties"][TAG_CLASS_ID]["multi_select"]["options"]
        
    node_list = []
    page_tags_list = []
    edge_rel_list = []
    web_list = []

    # { id: 0, label: "Myriel", group: 1 },
    # { id: 1, label: "Napoleon", group: 1 },

    # { from: 1, to: 0 },
    # { from: 2, to: 0 },

    existing_tagset = set()

    iteration = 0
    for page in pages_info:
        _tags = []
        try:
            for tag in page["properties"][TAG_CLASS_ID]["multi_select"]:
                _tags.append(tag['name'])

            _node = {
                "id" : iteration,
                "label" : page["properties"]["Name"]["title"][0]["plain_text"].replace('\n', ' '),
                "group" : 0,
                "weburl" : page['url'],
                "tags" : _tags,
            }

        except:
            continue
        
        iteration += 1
        
        node_list.append(_node)
        page_tags_list.append(_tags)
        web_list.append(page["url"])

        existing_tagset.update(_tags)

    existing_tagset.add("NOTAG")
    n_tags = len(existing_tagset)
    _tag_color_list = [randomcolorfromint(i, n_tags) for i in range(len(existing_tagset) + 1)]
    tag_color_map = {tag: color for tag, color in zip(existing_tagset, _tag_color_list)}
    
    for idx, node in enumerate(node_list):
        if len(page_tags_list[idx]) > 0:
            node["color"] = avg_color([tag_color_map[_tag] for _tag in page_tags_list[idx]])
        else:
            node["color"] = tag_color_map["NOTAG"]


    for idx, nodei in enumerate(node_list):
        tag_i = page_tags_list[idx]

        for jdx, nodej in enumerate(node_list):
            if idx <= jdx:
                continue
            tag_j = page_tags_list[jdx]

            # if there are common tags, add edge
            intersection = set(tag_i).intersection(tag_j)

            if len(intersection) > 0:
                avg_tagset_color = avg_color([tag_color_map[_tag] for _tag in intersection])
                strength = (1 - (len(intersection)/(len(set(tag_i) | set(tag_j))))) * 100
                edge_rel_list.append({"from": idx, "to": jdx, "length": strength, "color" : avg_tagset_color})
    
    
    

    print(len(node_list))


    return node_list, edge_rel_list, page_tags_list, web_list


@app.get("/update_cache")
def cache_all():
    save_page_metainfo_json()
    cache_allpage_info_json()
    generate_graphinfo()




@app.get('/graph_info')
def get_graph_info():
    node_list, edge_rel_list, page_tags_list, web_list = generate_graphinfo()
    return {
        "nodes": node_list,
        "edges": edge_rel_list,
        "tags": page_tags_list,
        "webs": web_list,
    }


if __name__ == "__main__":
    cache_allpage_info_json()