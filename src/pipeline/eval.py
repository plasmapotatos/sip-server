import json
import random
import av
import cv2
import re
import numpy as np
from loader import load_answer_files
from agent import update_evaluation_json, update_evaluation_json_custom
from request import BaselineModel, VideoLLaVA
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm
import statistics
from gradio_client import Client

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
        # convert 1-indexed to 0-indexed
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
    # calculate and get metrics
    tp, tn, fp, fn = 0, 0, 0, 0
    for i in range(len(y_true)):
        if(len(results[i]) > 1):
            if(results[i][:1] == 'Y'):
                fp += 1
            else: 
                fn += 1
        elif(y_true[i] != results[i]):
            if(y_true[i] == 'N'):
                fp += 1
            else:
                fn += 1
        else:
            if(y_true[i] == 'N'):
                tn += 1
            else:
                tp += 1

    precision = tp/(tp + fp) if(tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    #return metrics in dictionary
    return {
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn,
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

def get_frames_llava(video_path):
    container = av.open(video_path)
    video = cv2.VideoCapture(video_path)

    total_frames = container.streams.video[0].frames
    indices = np.arange(0, total_frames, container.streams.video[0].average_rate).astype(int)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    times = indices/fps

    return indices.tolist(), times.tolist()

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

def extract_text_between_tags(input_string):
    pattern = r"<output>(.*?)<\/output>"
    matches = re.findall(pattern, input_string)
    return matches

def get_pred_conf(output):
    try:
        for i in range(len(output) - 1, -1, -1):
            if(output[i:i + 1] == "Y" or output[i:i + 1] == "N"):
                return output[i:i + 1]
    except:
        return "ERROR"
    return "No output found"

if __name__ == '__main__':
    vid_directory = './data/Videos'
    out_file = './src/pipeline/eval_array.json'
    grnd_truth_directory="./data/Annotation_files"
    separate_file = './src/pipeline/all_eval_results.json'
    conf_file = './src/pipeline/confidence_results.json'

    seconds_per_frame = 1 # for GPT-4o

    model = BaselineModel()
    mode = "safety"

    total_precision = []
    total_recall = []
    total_f1 = []
    # client = Client("http://127.0.0.1:7860")

    failure_cases = []
    conf_results = []
    conf_list = []
    low_conf_list = []

    total_true_pos = 0
    total_true_neg = 0
    total_false_pos = 0
    total_false_neg = 0

    for i in tqdm(range(1, 3)):
        k = random_vid_indices(3)

        print(k)
        while (True):
            try: 
                # if(isinstance(model, VideoLLaVA)):
                #     update_evaluation_json_custom(video_directory=vid_directory, output_file=out_file, model=model, vidnums=k, mode=mode, client=client)
                if(isinstance(model, BaselineModel)):
                    update_evaluation_json_custom(video_directory=vid_directory, output_file=out_file, model=model, vidnums=k, mode=mode)
                break
            except Exception as e:
                print("Error!", e)
                continue
        
        # get results array (res) from json file
        with open(out_file, 'r') as f:
            results = json.load(f)

        if(isinstance(model, VideoLLaVA)):
            for i2 in range(len(results)):
                try:
                    results[i2] = results[i2].split('ASSISTANT: ')[1]
                except:
                    print("I hate errors")
        
        predictions = []
        for r in results:
            if mode == "safety":
                processed_result = extract_text_between_tags(r)
                print("Processed result: ", processed_result)
                if len(processed_result) > 0:
                    predictions.append(processed_result[0])
                    continue
                else:
                    print("No output found: ", r)
                    predictions.append("N")
                    continue

                # if "has fallen" in r or "have fallen" in r:
                #     predictions.append("Y")
                # elif "Activity of Daily Living" in r or "Activities of Daily Living" in r or "activity of daily living" in r or "activities of daily living" in r or "not fall" in r:
                #     predictions.append("N")
                # else:
                #     predictions.append("Y")
            if mode == "default":
                if(r[:1] == 'Y' or r[:1] == 'N'):
                    predictions.append(r[:1])
                    continue
                
                if "has fallen" in r or "have fallen" in r:
                    predictions.append("Y")
                elif "Activity of Daily Living" in r or "Activities of Daily Living" in r or "activity of daily living" in r or "activities of daily living" in r or "not fall" in r:
                    predictions.append("N")
                else:
                    predictions.append("Y")

        y_true = get_y_true_custom("./data/Annotation_files", k)

        for j in range(len(k)):
            video_path = "./data/Videos/video_(" + str(k[j]) + ").avi"

            frames, frametimes = get_frames(video_path, seconds_per_frame)
            ans = ''
            while (True):
                try: 
                    ans = BaselineModel().eval_consistency(video_path, frames, results[j])
                    break
                except Exception as e:
                    print("Error!", e)
                    continue

            conf = float(re.search("[01][.][0-9]+", ans).group())
            edu_pred = get_pred_conf(ans)
            conf_dict = {
                "batch_id": i,
                "ground_truth": y_true[j],
                "model_output": results[j],
                "model_prediction": predictions[j],
                "confidence_score": conf,
                "confidence_score_explanation": ans,
                "educated_prediction": edu_pred
            }

            conf_list.append(conf)
            conf_results.append(conf_dict)

            low_conf = False
            conflict = False
            
            if(conf < 0.5):
                low_conf_list.append(conf_dict)
                low_conf = True
                predictions[j] += '(low confidence)'
            if(ans[-1:] != predictions[j]):
                conflict = True
                predictions[j] += '(conflict)'
                if(not low_conf):
                    low_conf_list.append(conf_dict)
            
            if(predictions[j] == y_true[j] and predictions[j] == ans[-1:] and not low_conf and not conflict):
                continue
            
            seconds_per_frame = 1

            faildict = {
                "batch_id": i,
                "ground_truth": y_true[j],
                "model_output": results[j],
                "model_prediction": predictions[j],
                "false_positive": predictions[j][:1] == 'Y',
                "false_negative": predictions[j][:1] == 'N',
                "video_number": k[j],
                "video_path":video_path,
                "frame_numbers": frames,
                "time_of_frames(seconds)": frametimes,
                "confidence_score": conf,
                "educated_prediction": edu_pred,
                "confidence_score_explanation": ans
            }

            failure_cases.append(faildict)

        #run the evaluate() function to get a dictionary of metrics
        evaluation_metrics = evaluate(y_true, predictions)

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
            'True Positive Count': evaluation_metrics['tp'],
            'True Negative Count': evaluation_metrics['tn'],
            'False Positive Count': evaluation_metrics['fp'],
            'False Negative Count': evaluation_metrics['fn'],
            'Precision': evaluation_metrics['precision'],
            'Recall': evaluation_metrics['recall'],
            'F1 Score': evaluation_metrics['f1_score']
        }
        data.append(new_dict)

        with open(separate_file, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        total_true_neg += evaluation_metrics['tn']
        total_true_pos += evaluation_metrics['tp']
        total_false_pos += evaluation_metrics['fp']
        total_false_neg += evaluation_metrics['fn']
    
    with open(separate_file, 'r') as file:
        data = json.load(file)

    total_precision = []
    total_recall = []
    total_f1 = []

    for dict1 in data:
        total_precision.append(dict1['Precision'])
        total_recall.append(dict1['Recall'])
        total_f1.append(dict1['F1 Score'])

    with open(separate_file, 'r') as file:
        data = json.load(file)
    
    new_dict = {
        'id': 'Failure Cases',
        'failure_cases': failure_cases
    }

    data.append(new_dict)

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

    with open(separate_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    new_dict = {
        'id': 'Failure Cases',
        'failure_cases': low_conf_list
    }
    conf_results.append(new_dict)
    
    new_dict = {
        'ID': 'Final Evaluation',
        'Mean': statistics.mean(conf_list),
        'Standard Deviation': statistics.stdev(conf_list)
    }

    conf_results.append(new_dict)

    with open(conf_file, 'w') as outfile:
        json.dump(conf_results, outfile, indent=4)
