import v1
import json


def example():
    hostname = "www14.v1host.com"
    instance = "v1sdktesting"
    is_https = True
    port = 443

    username = "admin"
    password = "admin"

    connection = v1.V1(hostname, instance, port, is_https)
    v = connection.with_creds(username, password)

    created_story = v.create("Story", {
        "Name": "Walker's created python SDK story",
        "Scope": "Scope:0"
    })
    created_story = json.loads(created_story)
    print(created_story)

    oid_parts = created_story["id"].split(":")

    created_story_id = oid_parts[0] + ":" + oid_parts[1]

    print(created_story_id)

    story_query = {
        "from": "Story",
        "select": ["Name"],
        "where": {
            "ID": created_story_id
        }
    }

    retrieved_story = json.loads(v.query(story_query))[0][0]
    print(retrieved_story)

    updated_story = v.update(retrieved_story["_oid"], {
        "Name": "Walker's Python SDK!"
    })

    print(updated_story)

if __name__ == "__main__":
    example()


