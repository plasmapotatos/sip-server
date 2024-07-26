import json
import random
import cv2
from loader import load_answer_files
from agent import update_evaluation_json, update_evaluation_json_custom
from request import BaselineModel
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm
import statistics

def get_y_true(ground_truth_directory):
    y_true = []
    y_true_files = load_answer_files(ground_truth_directory)

    # Wrapping the entire file processing loop with tqdm
    for file_path in tqdm(y_true_files, desc="Processing files", unit="file"):
        with open(file_path) as f:
            s = f.readline()

        try:
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
    y_true_files = load_answer_files(ground_truth_directory)
    
    # Wrapping the entire file processing loop with tqdm
    for n in vid_nums:
        with open(y_true_files[n - 1]) as f:
            s = f.readline()

        try:
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

def get_frames(video_path, seconds_per_frame):
    frames = []
    frame_times = []

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame=0
    curr_time=0.0

    # Loop through the video and extract frames at specified sampling rate
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        frames.append(curr_frame)
        frame_times.append(curr_time)
        curr_frame += frames_to_skip
        curr_time += seconds_per_frame
    video.release()
    
    return frames, frame_times

if __name__ == '__main__':
    vid_directory = './data/Videos'
    out_file = './src/pipeline/eval_array.json'
    grnd_truth_directory="./data/Annotation_files"
    separate_file = './src/pipeline/all_eval_results.json'

    seconds_per_frame = 1 # for GPT-4o

    total_precision = []
    total_recall = []
    total_f1 = []

    failure_cases = []

    total_true_pos = 0
    total_true_neg = 0
    total_false_pos = 0
    total_false_neg = 0

    for i in range(1, 11):
        k = random_vid_indices(30)

        print(k)
        while (True):
            try: 
                update_evaluation_json_custom(video_directory=vid_directory, output_file=out_file, model=BaselineModel('gpt-4o', seconds_per_frame=seconds_per_frame), vidnums=k)
                break
            except Exception as e:
                print("Error!", e)
                continue
        
        # get results array (res) from json file
        with open(out_file, 'r') as f:
            results = json.load(f)

        predictions = []

        for n in results:
            predictions.append(n[:1])

        y_true = get_y_true_custom("./data/Annotation_files", k)
        #run the evaluate() function to get a dictionary of metrics
        evaluation_metrics = evaluate(y_true, predictions)

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

        false_pos = 0
        true_pos = 0
        false_neg = 0
        true_neg = 0

        for j in range(len(k)):
            if(predictions[j] == y_true[j]):
                if(predictions[j] == 'Y'): 
                    true_pos += 1
                else:
                    true_neg += 1
                continue
            
            if(y_true[j] == 'N'):
                false_pos += 1
            else:
                false_neg += 1
            
            video_path = "./data/Videos/video_(" + str(k[j]) + ").avi"
            seconds_per_frame = 1

            frames, frametimes = get_frames(video_path, seconds_per_frame)
            
            faildict = {
                "batch_id": i,
                "ground_truth": y_true[j],
                "model_output": results[j],
                "model_prediction": predictions[j],
                "false_positive": y_true[j] == 'N',
                "false_negative": y_true[j] == 'N',
                "video_number": k[j],
                "video_path":video_path,
                "frame_numbers": frames,
                "time_of_frames(seconds)": frametimes
            }

            failure_cases.append(faildict)

        new_dict = {
            'ID': i,
            'Video IDs': k,
            'Model Predictions': results,
            'Ground Truth': y_true,
            'True Positive Count': true_pos,
            'True Negative Count': true_neg,
            'False Positive Count': false_pos,
            'False Negative Count': false_neg,
            'Precision': evaluation_metrics['precision'],
            'Recall': evaluation_metrics['recall'],
            'F1 Score': evaluation_metrics['f1_score']
        }
        data.append(new_dict)

        with open(separate_file, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        
        total_true_neg += true_neg
        total_true_pos += true_pos
        total_false_pos += false_pos
        total_false_neg += false_neg
    
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
        'Total True Positive': total_true_pos,
        'Total True Negative': total_true_neg,
        'Total False Positive': total_false_pos,
        'Total False Negative': total_false_neg,
        'Precision (Mean)': statistics.mean(total_precision),
        'Precision (Standard Deviation)': statistics.stdev(total_precision),
        'Recall (Mean)': statistics.mean(total_recall),
        'Recall (Standard Deviation)': statistics.stdev(total_recall),
        'F1 Score (Mean)': statistics.mean(total_f1),
        'F1 Score (Standard Deviation)': statistics.stdev(total_f1)
    }
    data.append(new_dict)

    new_dict = {
        'id': 'Failure Cases',
        'failure_cases': failure_cases
    }

    data.append(new_dict)

    with open(separate_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)