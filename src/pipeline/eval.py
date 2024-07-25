import json
import random
from loader import load_answer_files
from agent import update_evaluation_json, update_evaluation_json_custom
from request import BaselineModel, VideoLLaVA
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm
import statistics
from gradio_client import Client

def get_y_true(ground_truth_directory):
    y_true = []
    firstlines = []

    y_true_files = load_answer_files(ground_truth_directory)

    # Wrapping the entire file processing loop with tqdm
    for file_path in tqdm(y_true_files, desc="Processing files", unit="file"):
        with open(file_path) as f:
            s = f.readline()

        try:
            firstlines.append(s)
            if(s == 'Fall\n'):
                y_true.append('Y')
            elif(s == 'ADL\n' or int(s) == 0):
                y_true.append('N')
            else:
                y_true.append('Y')
        except:
            y_true.append('N')

        f.close()
    
    return y_true

def get_y_true_custom(ground_truth_directory, vid_nums):
    y_true = []
    firstlines = []

    y_true_files = load_answer_files(ground_truth_directory)
    
    # Wrapping the entire file processing loop with tqdm
    for n in vid_nums:
        with open(y_true_files[n]) as f:
            s = f.readline()

        try:
            firstlines.append(s)
            if(s == 'Fall\n'):
                y_true.append('Y')
            elif(s == 'ADL\n' or int(s) == 0):
                y_true.append('N')
            else:
                y_true.append('Y')
        except:
            y_true.append('N')

        f.close()
    
    return y_true

def evaluate(y_true, results):
    # y_true = answers
    # calculate and get metrics
    precision = precision_score(y_true, results, average='weighted')
    recall = recall_score(y_true, results, average='weighted')
    f1 = f1_score(y_true, results, average='weighted')

    #return metrics in dictionary
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

def random_vid_indices(numofvids):
    vidnums = []

    while(len(vidnums)<numofvids):
        n = random.randint(1, 330)
        if(vidnums.count(n) == 0):
            vidnums.append(n)

    return vidnums


if __name__ == '__main__':
    vid_directory = './data/Videos'
    out_file = './src/pipeline/eval_array.json'
    grnd_truth_directory="./data/Annotation_files"
    separate_file = './src/pipeline/videollava_eval.json'

    total_precision = []
    total_recall = []
    total_f1 = []
    client = Client("http://127.0.0.1:7860")

    for i in range(1, 3):
        k = random_vid_indices(3)

        print(k)
        update_evaluation_json_custom(video_directory=vid_directory, output_file=out_file, model=VideoLLaVA('Video-LLaVA'), vidnums=k, client=client)

        # get results array (res) from json file
        with open(out_file, 'r') as f:
            results = json.load(f)
        
        predictions = []
        for r in results:
            predictions.append(r.split('ASSISTANT: ')[1][:1])

        y_true = get_y_true_custom("./data/Annotation_files", k)
        #run the evaluate() function to get a dictionary of metrics
        evaluation_metrics = evaluate(y_true, predictions)

        print("Fall Count: " + str(y_true.count("Y")))
        print("ADL Count: " + str(y_true.count("N")))
        print(y_true)
        # print('\n')

        print("Fall Count: " + str(predictions.count("Y")))
        print("ADL Count: " + str(predictions.count("N")))
        print(predictions)

        #print metrics
        print(f"Precision: {evaluation_metrics['precision']:.3f}")
        print(f"Recall: {evaluation_metrics['recall']:.3f}")
        print(f"F1 Score: {evaluation_metrics['f1_score']:.3f}")

        total_precision.append(evaluation_metrics['precision'])
        total_recall.append(evaluation_metrics['recall'])
        total_f1.append(evaluation_metrics['f1_score'])
        try:
            with open(separate_file, 'r') as file:
                data = json.load(file)
        except Exception as e:
            print(e)
            data = []
        
        new_dict = {
            'ID': i,
            'Video IDs': k,
            'Model Output': results,
            'Model Predictions': predictions,
            'Ground Truth': y_true,
            'Precision': evaluation_metrics['precision'],
            'Recall': evaluation_metrics['recall'],
            'F1 Score': evaluation_metrics['f1_score']
        }
        data.append(new_dict)

        with open(separate_file, 'w') as outfile:
            json.dump(data, outfile, indent=4)
    
    with open(separate_file, 'r') as file:
        data = json.load(file)

    total_precision = []
    total_recall = []
    total_f1 = []

    for dict1 in data:
        total_precision.append(dict1["Precision"])
        total_recall.append(dict1["Recall"])
        total_f1.append(dict1["F1 Score"])

    print(total_precision)
    print(total_recall)
    print(total_f1)

    print(statistics.mean(total_precision))
    print(statistics.stdev(total_precision))

    print(statistics.mean(total_recall))
    print(statistics.stdev(total_recall))

    print(statistics.mean(total_f1))
    print(statistics.stdev(total_f1))

    with open(separate_file, 'r') as file:
        data = json.load(file)

    new_dict = {
        'id': 'Final Evaluation',
        'Precision (Mean)': statistics.mean(total_precision),
        'Precision (Standard Deviation)': statistics.stdev(total_precision),
        'Recall (Mean)': statistics.mean(total_recall),
        'Recall (Standard Deviation)': statistics.stdev(total_recall),
        'F1 Score (Mean)': statistics.mean(total_f1),
        'F1 Score (Standard Deviation)': statistics.stdev(total_f1)
    }
    data.append(new_dict)

    with open(separate_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)