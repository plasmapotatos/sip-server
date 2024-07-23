datasetlist = []

le2i = {
    "dataset": "Le2i",
    "data": []
}

for i in range(1, 71):
    dict1 = {
        "id": i,
        "filepath": "./data/Videos/video_(" + str(i) + ").avi",
        "location": "Coffee Room",
        "groundtruth": "yes"
    }

    le2i["data"].append(dict1)

for i in range(71, 131):
    dict1 = {
        "id": i,
        "filepath": "./data/Videos/video_(" + str(i) + ").avi",
        "location": "Home",
        "groundtruth": "yes"
    }

    le2i["data"].append(dict1)

datasetlist.append(le2i)
#hola
