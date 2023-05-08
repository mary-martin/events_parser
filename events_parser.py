from html.parser import HTMLParser
import csv
import os
import json
import spacy
import multiprocessing as mp
from tqdm.contrib.concurrent import process_map
import argparse

nlp = spacy.load("en_core_web_lg")

# This script parses the html files in the unmatched_events directory and outputs the data to a csv file
# NOTE: Delete the generated csv file before running this script again, as the data will be appended to the existing csv file ('rm event_data_*' will do the trick)
# NOTE: Run this script from one of the subdirectories of the unmatched_events directory

class EventHTMLParser(HTMLParser):
    # If a line of html corresponds to a q_node, arg_1, or arg_2, etc., the corresponding flag is set to True
    flags = {
        "q_node": False,
        "arg_1": False,
        "arg_2": False,
        "arg_3": False,
        "mention": False,
        "text": False,
    }

    data_row = []
    mentions = ""

    def set_output_file(self, filename):
        self.csv_file = filename

    def handle_data(self, data):
        data = data.strip()
        if data:
            # print("Data:", data)
            self.check_data(data, "QNode:", "q_node")
            self.check_data(data, "Argument #1:", "arg_1")
            self.check_data(data, "Argument #2:", "arg_2")
            self.check_data(data, "Argument #3:", "arg_3")
            self.check_data(data, "Event Mentions:", "mention")
            self.check_data(data, ", Text:", "text")

    def check_data(self, data, target, label):
        if self.flags[label]:
            # print(label,':', data)
            # If we have reached the end of a q_node, we need to write the data to the csv file as a new row
            if label == "q_node" and self.data_row != []:
                if output_csv:
                    if self.data_row[0] not in repeated_nodes.keys():
                        data_to_csv(self.data_row, self.csv_file)
                    else:
                        data_to_csv(self.data_row, filename="repeated_nodes.csv")
                
                if data in all_nodes:
                    # first record the repeated node
                    if data not in repeated_nodes.keys():
                        repeated_nodes[data] = [1]
                        if output_csv:
                            data_to_csv(self.data_row, filename="repeated_nodes_args.csv")
                    else:
                        repeated_nodes[data][0] += 1
                else:
                    all_nodes.append(data)
                
                # create new row
                self.data_row = []
                self.data_row.append(data)
                self.flags[label] = False

            elif label == "mention":
                if "#1:" in data:
                    self.data_row.append(self.mentions)
                    self.mentions = ""
                    self.flags[label] = False
                else:
                    self.mentions += " " + data
            else:
                self.data_row.append(data)
                self.flags[label] = False
        # if we have reached a q_node, arg_1, or arg_2, etc., set the corresponding flag to True
        if data == target:
            self.flags[label] = True


def data_to_csv(row_data, filename):
    with open(filename, "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row_data)


### JSON parsing functions ###
# gets all q node names from json file
def get_all_events(data):
    events = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "name":
                events.append(v)
            else:
                events.extend(get_all_events(v))
    elif isinstance(data, list):
        for item in data:
            events.extend(get_all_events(item))

    if output_text:
        with open("original_nodes.txt", "w") as f:
            for item in events:
                f.write("%s\n" % item)
        return events


def get_all_event_elements(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        print(type(data))
    return get_all_events(data)


# check similarity between two strings
def check_similarity(args):
    type1, type2 = args
    if type1 != type2:
        doc1 = nlp(type1)
        doc2 = nlp(type2)
        similarity_score = doc1.similarity(doc2)
        if similarity_score > 0.7:
            line = [type1.lower(), type2.lower(), similarity_score]
            data_to_csv(line, filename="similarity_scores.csv")
            # print(line)
    else:
        print("Duplicate: ", type1)
        return

    return (type1, type2, similarity_score)


def compare_lists(types_x, types_y, num_processes=mp.cpu_count()):
    # Create a list of element pairs to compare
    elem_pairs = [(type1, type2) for type1 in types_x for type2 in types_y]
    print(len(elem_pairs))

    # Create a multiprocessing pool and map the similarity calculation function to the element pairs
    similarity_scores = process_map(
        check_similarity, elem_pairs, max_workers=num_processes
    )

    # Create a dictionary of similarity scores, only including scores above 0.7
    similarity_dict = {
        (type1, type2): similarity_score
        for type1, type2, similarity_score in similarity_scores
        if similarity_score > 0.7
    }

    return similarity_dict

def load_scores_as_dict(csv_path):
    data_dict = {}

    # Open the CSV file and read its contents
    with open(csv_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)

        # Iterate over each row in the CSV file
        for row in csvreader:
            # Use the first element of the row as the dictionary key
            key = (row[0], row[1])

            # Use the rest of the elements in the row as the associated values
            values = row[2]

            # Add the key-value pair to the dictionary
            data_dict[key] = values

    return data_dict


def main():
    # Define the argument parser
    parser = argparse.ArgumentParser(
        description="Output options for unmatched event procesing"
    )
    # Define the command-line arguments with default values
    parser.add_argument(
        "--csv", action="store_true", help="output CSV files", default=True,
    )
    parser.add_argument(
        "--text", action="store_true", help="output text files", default=True,
    )
    parser.add_argument(
        "--json_path",
        type=str,
        help="path to the input JSON file",
        default="/home/marymartin/Code/schema_enrichment/schemas/coup/coup.json",
    )
    parser.add_argument(
        "--similarity",
        action="store_true",
        help="flag to perform a similarity check, default is True",
        default=True,
    )
    parser.add_argument(
        "--similarity_type",
        type=str,
        help="load similarity scores, compare all events, compare repeated events, or compare unmatched events to themselves",
        default="repeated",
    )
    parser.add_argument(
        "--num_processes",
        type=int,
        help="number of processes to use for multiprocessing (only for similarity check)",
        default=mp.cpu_count(),
    )

    # Parse the command-line arguments
    args = parser.parse_args()
    json_path = args.json_path
    similarity_check = args.similarity
    similarity_type = args.similarity_type
    options=["all", "repeated", "load", "unmatched"]
    num_processes = args.num_processes

    # global variables for output options
    global output_csv
    output_csv = args.csv
    global output_text
    output_text = args.text

    # uncomment to delete and replace files from previous run
    os.system("rm event_data_*.csv")
    os.system("rm repeated_nodes_list.csv")
    os.system("rm repeated_nodes.csv")
    os.system("rm repeated_nodes_args.csv")
    os.system("rm *.txt")

    # These global variables are used to keep track of the q_nodes and repeated q_nodes
    global all_nodes
    all_nodes = []
    global repeated_nodes
    repeated_nodes = {}

    csv_idx = 0
    html_dir = os.getcwd()
    # iterate through html files in current directory
    for html_filename in os.listdir(html_dir):
        if html_filename.endswith(".html"):
            csv_file = "event_data_" + str(csv_idx) + ".csv"
            # path to html file
            file_path = html_dir + "/" + html_filename
            # read in html as str
            html_file = open(file_path, "r")
            index = html_file.read()
            # index = index.replace('<br>', '')
            html_file.close()
            # add header to csv
            field_names = [
                "q_node",
                "mentions",
                "arg_1",
                "text",
                "arg_2",
                "text",
                "arg_3",
                "text",
            ]
            if output_csv:
                data_to_csv(field_names, filename=csv_file)
            # parse + output to csv
            parser = EventHTMLParser()
            parser.set_output_file(csv_file)
            parser.feed(index)
            print(html_filename, ":", csv_idx)
            csv_idx += 1

    original_nodes = get_all_event_elements(json_path)

    print("Num. repeated nodes:", len(repeated_nodes.keys()))
    print("Num. unique nodes:", len(all_nodes))
    print("Num original nodes:", len(original_nodes))

    # remove underscores from unmatched events
    repeats_edited = {}
    for item in repeated_nodes.keys():
        new_item = item.replace("_", " ")
        repeats_edited[new_item] = repeated_nodes[item]

    # remove underscores from all nodes
    for type in all_nodes:
        new_type = type.replace("_", " ")
        all_nodes[all_nodes.index(type)] = new_type

    if similarity_check:
        if similarity_type == "repeated":
            # compare original nodes to repeated nodes
            similarity_dict = compare_lists(repeats_edited, original_nodes, num_processes)

        elif similarity_type == "all":
            # compare all nodes to original nodes
            similarity_dict = compare_lists(all_nodes, all_nodes, num_processes)
        
        elif similarity_type == "load":
            # load similarity scores from csv
            similarity_dict = load_scores_as_dict("similarity_scores.csv")
        
        elif similarity_type == "unmatched":
            # compare unmatched nodes to themselves
            similarity_dict = compare_lists(all_nodes, all_nodes, num_processes)
        elif similarity_type not in options:
            print("Please enter a valid similarity type")
            return

        print(similarity_dict)
        for type1, type2 in similarity_dict.keys():
            if type2 not in repeats_edited[type1]:
                repeats_edited[type1].append(type2)

        print(repeats_edited)
        repeats_file = "repeated_nodes_list.csv"
        for item in repeats_edited.keys():
            row_data = repeats_edited[item]
            row_data.insert(0, item)
            if(output_csv):
                data_to_csv(row_data, filename=repeats_file)

    # print(similarity_dict)

if __name__ == "__main__":
    main()
