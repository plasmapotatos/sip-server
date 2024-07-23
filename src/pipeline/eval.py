import json
import random
from loader import load_answer_files
from agent import update_evaluation_json, update_evaluation_json_custom
from request import BaselineModel
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm
import statistics

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

def bane_of_my_existence():
    vidnums = []

    while(len(vidnums)<30):
        n = random.randint(1, 330)
        if(vidnums.count(n) == 0):
            vidnums.append(n)

    return vidnums


if __name__ == '__main__':
    vid_directory = './data/Videos'
    out_file = './src/pipeline/eval_array.json'
    grnd_truth_directory="./data/Annotation_files"
    separate_file = './src/pipeline/all_eval_results.json'

    total_precision = []
    total_recall = []
    total_f1 = []

    for i in range(11, 11):
        k = bane_of_my_existence()

        print(k)
        update_evaluation_json_custom(video_directory=vid_directory, output_file=out_file, model=BaselineModel('gpt-4o'), vidnums=k)

        # get results array (res) from json file
        with open(out_file, 'r') as f:
            results = json.load(f)

        y_true = get_y_true_custom("./data/Annotation_files", k)
        #run the evaluate() function to get a dictionary of metrics
        evaluation_metrics = evaluate(y_true, results)

        print("Fall Count: " + str(y_true.count("Y")))
        print("ADL Count: " + str(y_true.count("N")))
        print(y_true)
        # print('\n')

        print("Fall Count: " + str(results.count("Y")))
        print("ADL Count: " + str(results.count("N")))
        print(results)

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
            'Model Predictions': results,
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