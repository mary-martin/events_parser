# HTML Event Processing Script

This script processes HTML unmatched event data to produce several output files. It must be run in the same directory as the HTML files.

## [Additional Documentation](additional_doc.md)

## Output Files

- `event_data_<file no.>.csv`: One file is produced for each HTML file. Each row contains an event name, mention, arguments, and participants.
- `original_nodes.txt`
- `repeated_nodes.csv`: Contains all instances of a repeated event except the first.
- `repeated_nodes_args.csv`: Contains one instance of each repeated event and its corresponding arguments.
- `repeated_nodes_list.csv`: Has a list of all repeated events and their frequency, along with any events from the original JSON file that score > 0.7 similarity (appended to the row).
- `similarity_scores.csv`: Each row contains similarity scores (out of 1) that are greater than 0.7 following each pair of compared events.

## Requirements

- Python 3.7 
- Required package: `spacy`. 
    - Before, first download the `en_core_web_lg` model:
```bash
python -m spacy download en_core_web_lg
```

## Arguments

- `csv` (optional): Whether to output CSV files. Default is `True`.
- `text` (optional): Whether to output text files. Default is `True`.
- `json_path` (required): Path to schema.
- `similarity` (optional): Whether to perform similarity check. Default is `True`.
- `similarity_type` (optional): Load similarity scores, compare all events, compare repeated events, or compare unmatched events to themselves. By default set to `repeated`.
  - Options: `load`, `all`, `repeated`, `unmatched`.
- `num_processes` (optional): Similarity check is done using multiprocessing. `num_processes` is set to `cpu_count()` by default.
  - The default value will require all CPUs, so it must be changed if you'd like to avoid this. This is done to speed up processing as the number of comparisons happening can be extremely large.

## Example

```bash
python process_html.py \
    --csv \
    --text \
    --json_path /home/marymartin/Code/schema_enrichment/schemas/chemical_spills/chemical_spills.json \
    --similarity \
    --similarity_type repeated \
    --num_processes 4 \
```

## Additional Notes

- The generated CSV and text files must be deleted before running this script again, as the data will be appended to the existing CSV files. If you run it again in the same directory, uncomment the `os.system()` calls in the main function of the script to automatically delete these.
- Example output is shown in the `examples/` directory. These files were generated from the unmatched events for 'coup'.