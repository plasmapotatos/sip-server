import json
import statistics
from eval import get_y_true_custom, evaluate, get_frames, get_frames_llava

infile = './src/pipeline/all_eval_results.json'
outfile = './src/pipeline/samllava_2August2024.json'
infileconf = './src/pipeline/confidence_results.json'
outfileconf = './src/pipeline/samllava_confidence_2August2024.json'
grnd_truth_directory="./data/Annotation_files"

data = []
conf_res = []
conf_list = []
low_conf_list = []
failure_cases = []
prelist, reclist, f1list = [], [], []

ttp, ttn, tfp, tfn = 0, 0, 0, 0
gndp = 0
gndn = 0

def get_pred_conf(output):
    try:
        for i in range(len(output) - 1, -1, -1):
            if(output[i:i + 1] == "Y" or output[i:i + 1] == "N"):
                return output[i:i + 1]
    except:
        return "ERROR"
    return "No output found"

with open(infile, 'r') as f:
    data = json.load(f)

with open(infileconf, 'r') as f:
    conf_res = json.load(f)

for i in range(10):
    evaldict = data[i]

    output = evaldict["Model Output"]
    predictions = evaldict["Model Predictions"]

    gndp += evaldict["Ground Truth"].count("Y")
    gndn += evaldict["Ground Truth"].count("N")

    y_true = get_y_true_custom(grnd_truth_directory, evaldict["Video IDs"])
    
    for j in range(30):
        confdict = conf_res[i * 30 + j]
        video_path = "./data/Videos/video_(" + str(evaldict["Video IDs"][j]) + ").avi"
        frames, frametimes = get_frames_llava(video_path)

        conf_list.append(confdict["confidence_score"])

        r = output[j]

        if "has fallen" in r or "have fallen" in r:
            predictions[j] = "Y"
        elif "Activity of Daily Living" in r or "Activities of Daily Living" in r or "activity of daily living" in r or "activities of daily living" in r or "not fall" in r or "Activities of Daily Life" in r or "Activity of Daily Life" in r or "activity of daily life" in r:
            predictions[j] = "N"
        else:
            predictions[j] = "Y"

        try:
            output[j] = output[j].split("ASSISTANT:")[1]
        except:
            output[j] = output[j]

        low_conf = False

        if(confdict["confidence_score"] < 0.5):
            low_conf_list.append(confdict)
            predictions[j] += '(low confidence)'
            low_conf = True
        if(get_pred_conf(confdict["confidence_score_explanation"]) != predictions[j][:1]):
            predictions[j] += '(conflict)'
            if(not low_conf):
                low_conf_list.append(confdict)

        if(predictions[j] != y_true[j]):
            faildict = {
                "batch_id": i + 1,
                "ground_truth": y_true[j],
                "model_output": output[j],
                "model_prediction": predictions[j],
                "false_positive": predictions[j][:1] == 'Y',
                "false_negative": predictions[j][:1] == 'N',
                "video_number": evaldict["Video IDs"][j],
                "video_path": video_path,
                "frame_numbers": frames,
                "time_of_frames(seconds)": frametimes,
                "confidence_score": confdict["confidence_score"],
                "educated_prediction": get_pred_conf(confdict["confidence_score_explanation"]),
                "confidence_score_explanation": confdict["confidence_score_explanation"]
            }

            failure_cases.append(faildict)
        
    results = evaluate(y_true, predictions)

    evaldict["Model Predictions"] = predictions
    evaldict["Model Output"] = output
    evaldict['True Positive Count'] = results['tp']
    evaldict['True Negative Count'] = results['tn']
    evaldict['False Positive Count'] = results['fp']
    evaldict['False Negative Count'] = results['fn']
    evaldict['Precision'] = results["precision"]
    evaldict['Recall'] = results["recall"]
    evaldict['F1 Score'] = results["f1_score"]

    ttp += results['tp']
    ttn += results['tn']
    tfp += results['fp']
    tfn += results['fn']

    prelist.append(results["precision"])
    reclist.append(results["recall"])
    f1list.append(results["f1_score"])

    data[i] = evaldict

data[10]["failure_cases"] = failure_cases

new_dict = {
    'id': 'Final Evaluation',
    'Total True Positive': ttp,
    'Total True Negative': ttn,
    'Total False Positive': tfp,
    'Total False Negative': tfn,
    'Precision (Mean)': statistics.mean(prelist),
    'Precision (Standard Deviation)': statistics.stdev(prelist),
    'Recall (Mean)': statistics.mean(reclist),
    'Recall (Standard Deviation)': statistics.stdev(reclist),
    'F1 Score (Mean)': statistics.mean(f1list),
    'F1 Score (Standard Deviation)': statistics.stdev(f1list)
}

data[11] = new_dict

new_dict = {
    'id': 'Failure Cases',
    'failure_cases': low_conf_list
}
conf_res.append(new_dict)
    
new_dict = {
    'ID': 'Final Evaluation',
    'Mean': statistics.mean(conf_list),
    'Standard Deviation': statistics.stdev(conf_list)
}
conf_res.append(new_dict)

with open(outfile, 'w') as f:
    json.dump(data, f, indent=4)

with open(outfileconf, 'w') as f:
    json.dump(conf_res, f, indent=4)

print("Ground Truth Positive: " + str(gndp))
print("Ground Truth Negative: " + str(gndn))