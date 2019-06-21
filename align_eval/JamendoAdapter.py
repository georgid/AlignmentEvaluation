import librosa
import glob
import os
import os.path
import csv

def convert_annotations(jamendo_dataset_path, annotation_output_path):
    '''
    For the given Jamendolyrics dataset base directory, convert all annotations to the MIREX lab format and output them into a given output directory
    :param jamendo_dataset_path: Base directory of jamendolyrics dataset
    :param annotation_output_path: Folder where lab files should be saved into
    :return:
    '''
    if not os.path.exists(annotation_output_path):
        os.makedirs(annotation_output_path)
    for onset_path in glob.glob(os.path.join(jamendo_dataset_path, "annotations", "*.wordonset.txt")):
        with open(onset_path, "r") as onset_file:
            # Get word onsets
            onsets = list(csv.reader(onset_file))
            onsets = [item[0] for item in onsets]

        # Offsets
        offsets = onsets[1:]
        y, sr = librosa.load(onset_path.replace("annotations", "mp3").replace("wordonset.txt", "mp3"), sr=None, mono=True)
        duration = float(len(y)) / float(sr)
        offsets.append(str(duration))

        # Get words
        with open(onset_path.replace("annotations", "lyrics").replace("wordonset", "words"), "r") as word_file:
            words = list(csv.reader(word_file))
            words = [item[0] for item in words]
        assert(len(words) == len(onsets))

        # Write files
        lab_path = os.path.join(annotation_output_path, os.path.basename(onset_path).replace(".wordonset.txt", ".wordonset.tsv"))
        with open(lab_path, "w") as lab_file:
            for idx in range(len(onsets)):
                lab_file.write(onsets[idx] + "," + offsets[idx] + "," + words[idx] + "\n")

def convert_predictions(jamendo_dataset_path, predictions_path, predictions_output_path):
    '''
    For the given predictions made according to Jamendolyrics dataset format (start, end timestamps), convert to the expected MIREX output format
    :param jamendo_dataset_path: Base directory of jamendolyrics dataset
    :param predictions_path: Predictions (ending in _align.csv, name is otherwise the same as the files in the jamendolyrics dataset)
    :param predictions_output_path: Folder where converted predictions should be saved
    :return:
    '''
    if not os.path.exists(predictions_output_path):
        os.makedirs(predictions_output_path)
    for onset_path in glob.glob(os.path.join(predictions_path, "*_align.csv")):
        with open(onset_path, "r") as onset_file:
            # Get onset and offset times
            onsets = list(csv.reader(onset_file))

        # Get words
        with open(os.path.join(jamendo_dataset_path, "lyrics", os.path.basename(onset_path).replace("_align.csv", ".words.txt")), "r") as word_file:
            words = list(csv.reader(word_file))
        assert(len(words) == len(onsets))
        preds = [onsets[i] + words[i] for i in range(len(onsets))]

        # Write lab file
        lab_path = os.path.join(predictions_output_path, os.path.basename(onset_path).replace("_align.csv", ".lab"))
        with open(lab_path, "w") as lab_file:
            for idx in range(len(onsets)):
                lab_file.write(str(preds[idx][0]) + "," + str(preds[idx][1]) + "," + str(preds[idx][2]) + "\n")

#convert_annotations("/home/daniel/Projects/jamendolyrics", "test")
#convert_predictions("/home/daniel/Projects/jamendolyrics", "/home/daniel/Projects/jamendolyrics/predictions/stoller_model", "test_pred")