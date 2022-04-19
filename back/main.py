
import os
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

def generate_graphinfo():
    
    # create tags map
    import json

    metainfo = json.load(open("env_metainfo.json"))
    pages_info = json.load(open("env_pages_info.json"))["results"]


    tagset = metainfo["properties"][TAG_CLASS_ID]["multi_select"]["options"]
        
    
    #print(tagset)

    node_list = []
    page_tags_list = []
    edge_rel_list = []
    web_list = []

    #   { id: 0, label: "Myriel", group: 1 },
    # { id: 1, label: "Napoleon", group: 1 },

    #   { from: 1, to: 0 },
  # { from: 2, to: 0 },

    existing_tagset = set()

    for idx, page in enumerate(pages_info):

        _node = {
            "id" : idx,
            "label" : page["properties"]["Name"]["title"][0]["plain_text"].replace('\n', ' '),
            "group" : 0,
        }

        _tags = []
        
        for tag in page["properties"][TAG_CLASS_ID]["multi_select"]:
            _tags.append(tag['name'])
        
        node_list.append(_node)
        page_tags_list.append(_tags)
        web_list.append(page["url"])

        existing_tagset.update(_tags)


    for idx in range(len(pages_info)):
        tag_i = page_tags_list[idx]
        for jdx in range(idx+1, len(pages_info)):
            tag_j = page_tags_list[jdx]
            # if there are common tags, add edge
            if len(set(tag_i).intersection(set(tag_j))) > 0:
                edge_rel_list.append({"from": idx, "to": jdx})
    
    tag_idx_map = {tag: idx for idx, tag in enumerate(existing_tagset)}
    for idx, node in enumerate(node_list):
        if len(page_tags_list[idx]) > 0:
            node["group"] = tag_idx_map[page_tags_list[idx][0]] + 1
        else:
            node["group"] = 0

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


