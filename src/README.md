# Script Folder

### The Pipeline

- Run `master_script.py` **from the root directory**

- Running the `master_script` executes python scripts in a following order:

  1. `parse_text.py` : parse SOP documents into json and csv

  2. `sop_topics_type_kmeans_tfidf.py` : run kmeans clustering on tfidf vectors of SOPs by event type

  3. `sop_topics_situation_kmeans_tfidf.py` : run kmeans clustering on tfidf vectors of SOPs by situation
  4. `type_flowchart.py` : generate flowchart of type level cluster results from step 2.
  5. `situ_flowchart.py`: generate flowchart of situation level cluster results from step 3.



### The Dashboard

- `situ_helper` : enables searching SOPs with input keywords using cosine similarity



### Scripts not included in the pipeline or dashboard:

- Entity Approach scripts:
  - `entity_preprocessor.py` : extract pre-defined entity patterns from SOP documents
  - `entity_model.py` : store the extracted entities into PATTERNS.JSONL file for `spacy.EntityRuler`

- `knowledge_map.py` : draw flowcharts of SOP documents that illustrate their hierarchical structures 
