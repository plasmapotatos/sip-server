import json
from loader import load_answer_files
from agent import update_evaluation_json
from request import BaselineModel
from sklearn.metrics import precision_score, recall_score, f1_score
from tqdm import tqdm

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

if __name__ == '__main__':
    vid_directory = './data/Videos'
    out_file = 'eval_array.json'
    grnd_truth_directory="./data/Annotation_files"

    # update_evaluation_json(video_directory=vid_directory, output_file=out_file, model=BaselineModel('gpt-4o'))

    # get results array (res) from json file
    with open('eval_array.json', 'r') as f:
        results = json.load(f)

    y_true = get_y_true(ground_truth_directory="./data/Annotation_files")
    #run the evaluate() function to get a dictionary of metrics
    evaluation_metrics = evaluate(y_true, results)

    print("Fall Count: " + str(y_true.count("Y")))
    print("ADL Count: " + str(y_true.count("N")))
    print(y_true)
    print('\n')

    print("Fall Count: " + str(results.count("Y")))
    print("ADL Count: " + str(results.count("N")))
    print(results)

    #print metrics
    print(f"Precision: {evaluation_metrics['precision']:.3f}")
    print(f"Recall: {evaluation_metrics['recall']:.3f}")
    print(f"F1 Score: {evaluation_metrics['f1_score']:.3f}")
