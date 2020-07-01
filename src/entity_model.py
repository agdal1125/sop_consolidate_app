import itertools
import spacy
from spacy.pipeline import EntityRuler
import entity_preprocesser
from entity_preprocesser import entity_rule_writer

class ent_model():

    def __init__(self, path_sop_folder = "/Users/Public/Desktop/SOPs/"):
        self.path_sop_folder = path_sop_folder

    def create(self, path_to_pattern_json, jargon_docx_path="/Users/jalee/Desktop/capstone-2020/utils/acronyms.docx"):
        """
        create a PATTERN.JSONL file

        Params
        ----
        path_to_pattern_json: str    path to write  and load the pattern rule from
        jargon_docx_path: str    path where acronyms.docx file is stored

        Returns
        ----
        spaCy model
        """
        self.path_to_pattern_json = path_to_pattern_json
        self.jargon_docx_path = jargon_docx_path
    
        entity_rule_writer(self.path_to_pattern_json, self.path_sop_folder, self.jargon_docx_path)

        print("PATTERN.JSONL file created")

        return


    def load(self, path_to_pattern_json="../notebook/entity_train/PATTERNS.JSONL"):
        """
        Incorporate PATTERN.JSONL file to the pretrained model for Named Entity Recognition
        
        Params
        ----
        path_to_pattern_json: str    path to write  and load the pattern rule from
        """
        self.path_to_pattern_json = path_to_pattern_json

        nlp = spacy.load("en_core_web_sm")
        ruler = EntityRuler(nlp).from_disk(path_to_pattern_json)
        nlp.add_pipe(ruler, before="ner")
        
        # Disable baseline ner
        nlp.disable_pipes('ner')
        
        self.ruler = ruler
        self.model = nlp

        return self


    def add_entity(self, label_list, pattern_list, save=False):
        """
        spaCy Rule-based matching wrapper.
        Add Entity Rule pattern to the EntityRuler object
        Refer to https://spacy.io/usage/rule-based-matching for more context

        Params
        ----
        label_list: list    list of Entity labels
        pattern_list: list    list of Entity patterns
        save: bool    Save the added entity pattern to JSONL file
        """
        assert len(label_list) == len(pattern_list)
        ent_rules = zip(label_list, pattern_list)
        patterns = []
        for lab, pat in ent_rules:
            patterns.append({"label":lab, "pattern":pat, "id":"custom"})
        self.ruler.add_patterns(patterns)

        if save:
            self.ruler.to_disk(self.path_to_pattern_json)
            
        return self

    
    def remove_entity(self, label_list, pattern_list, save=False):
        """
        spaCy Rule-based matching wrapper
        Remove Entity Rule pattern from JSONL file and re-read the file
        Refer to https://spacy.io/usage/rule-based-matching for more context

        Params
        ----
        label_list: list    list of Entity labels
        pattern_list: list    list of Entity patterns
        save: bool    Save the added entity pattern to JSONL file
        """
        assert len(label_list) == len(pattern_list)
        ent_rules = zip(label_list, pattern_list)
        patterns = []
        for lab, pat in ent_rules:
            patterns.append({"label":lab, "pattern":pat, "id":"custom"})
        
        all_patterns = self.ruler.patterns

        removed = list(itertools.filterfalse(lambda x: x in all_patterns, patterns)) \
                  + list(itertools.filterfalse(lambda x: x in patterns, all_patterns))
        
        self.model.disable_pipes("entity_ruler")
        self.ruler = EntityRuler(self.model)
        self.ruler.add_patterns(patterns)

        if save:
            self.ruler.to_disk(self.path_to_pattern_json)
            
        return self