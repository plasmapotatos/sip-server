import json
from loader import load_vids
from request import BaselineModel, VideoLLaVA

def run_validation(vid_directory, model):
    results = model.predict(directory=vid_directory)
    return results

def run_validation_custom(vid_directory, model, vidnums, client=None):
    results = model.predict_custom(directory=vid_directory, vidnums=vidnums, client=None)
    return results


def update_evaluation_json(video_directory, output_file, model):
    results = run_validation(video_directory, model)

    # adds data to json file in the form of a json array
    jarr = json.dumps(results)

    with open(output_file, 'w') as outfile:
        json.dump(results, outfile, indent=4)

def update_evaluation_json_custom(video_directory, output_file, vidnums, model, client=None):
    results = run_validation_custom(video_directory, model, vidnums, client=None)

    # adds data to json file in the form of a json array
    jarr = json.dumps(results)

    with open(output_file, 'w') as outfile:
        json.dump(results, outfile, indent=4)

if __name__ == '__main__':
    vid_directory = './src/pipeline/testing'
    out_file = 'eval_array.json'

    update_evaluation_json(video_directory=vid_directory, output_file=out_file)
    