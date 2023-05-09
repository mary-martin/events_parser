## Module: event_parser.py

The module parses HTML files in the unmatched_events directory and outputs the data to a CSV file.

### Functions:
1. `data_to_csv(row_data, filename)`:
    - This function writes a row of data to a CSV file.
    - Arguments:
        - `row_data`: list of strings representing the data for a row.
        - `filename`: string representing the name of the CSV file.
        
2. `get_all_events(data)`:
    - This function recursively searches a JSON data structure for all event names and returns them as a list of strings.
    - Argument:
        - `data`: JSON data structure.
    - Returns:
        - `events`: list of strings representing all event names in the JSON data structure.
    
3. `get_all_event_elements(filename)`:
    - This function loads a JSON file and calls the `get_all_events` function to return all event names.
    - Argument:
        - `filename`: string representing the name of the JSON file.
    - Returns:
        - `get_all_events(data)`: list of strings representing all event names in the JSON data structure.
    
4. `check_similarity(args)`:
    - This function checks the similarity between two strings using spaCy and returns a tuple of the two strings and their similarity score if the score is greater than 0.7.
    - Argument:
        - `args`: tuple of two strings to be compared.
    - Returns:
        - tuple of two strings and their similarity score if the score is greater than 0.7.
    
5. `compare_lists(types_x, types_y, num_processes)`:
    - This function creates a list of element pairs to compare and uses multiprocessing to map the similarity calculation function to the element pairs.
    - Arguments:
        - `types_x`: list of strings representing event names.
        - `types_y`: list of strings representing event names.
        - `num_processes`: integer representing the number of processes to use.
    - Returns:
        - `similarity_dict`: dictionary of element pairs and their similarity scores if the score is greater than 0.7.

### Classes:
1. `EventHTMLParser`:
    - This class extends HTMLParser to parse HTML files for event data.
    - Attributes:
        - `flags`: dictionary of flags indicating whether a line of HTML corresponds to a q_node, arg_1, arg_2, arg_3, mention, or text.
        - `data_row`: list of strings representing the data for a row.
        - `mentions`: string representing the mentions for an event.
        - `csv_file`: string representing the name of the CSV file.
    - Methods:
        - `set_output_file(self, filename)`:
            - This method sets the name of the CSV file to which the event data will be written.
            - Argument:
                - `filename`: string representing the name of the CSV file.
        - `handle_data(self, data)`:
            - This method handles a line of HTML data.
            - Argument:
                - `data`: string representing a line of HTML data.
        - `check_data(self, data, target, label)`:
            - This method checks whether a line of HTML data corresponds to a q_node, arg_1, arg_2, arg_3, mention, or text and updates the `data_row` attribute accordingly.
            - Arguments:
                - `data`: string representing a line of HTML data.
                - `target`: string representing the target text.
                - `label`: string representing the label of the flag to update.
        - `data_to_csv(row_data, filename)`:
            - This method writes a row of data to a CSV file.
