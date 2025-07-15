import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

class PartOfSpeech(Enum):
    NOUN = "noun"
    VERB = "verb"
    PARTICIPLE = "participle"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    ARTICLE = "article"
    PARTICLE = "particle"
    CONJUNCTION = "conjunction"
    PREPOSITION = "preposition"
    PRONOUN = "pronoun"
    NUMERAL = "numeral"
    INTERJECTION = "interjection"
    EXCLAMATION = "exclamation"
    PUNCTUATION = "punctuation"
    IRREGULAR = "irregular"

@dataclass
class Word:
    """Represents a word in the Greek text with all its linguistic attributes."""
    form: str
    lemma: str
    id: int
    parent_id: int
    sentence_id: int
    relation: str
    part_of_speech: Optional[str] = None
    person: Optional[str] = None
    number: Optional[str] = None
    tense: Optional[str] = None
    mood: Optional[str] = None
    voice: Optional[str] = None
    gender: Optional[str] = None
    case: Optional[str] = None
    degree: Optional[str] = None
    children: List['Word'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

class GreekTextParser:
    """Parses Perseus Treebank XML data into Word objects."""
    
    def __init__(self):
        self.postag_mappings = {
            'part_of_speech': {
                'n': 'noun', 'v': 'verb', 't': 'participle', 'a': 'adjective',
                'd': 'adverb', 'l': 'article', 'g': 'particle', 'c': 'conjunction',
                'r': 'preposition', 'p': 'pronoun', 'm': 'numeral', 'i': 'interjection',
                'e': 'exclamation', 'u': 'punctuation', 'x': 'irregular'
            },
            'person': {'1': 'first', '2': 'second', '3': 'third'},
            'number': {'s': 'singular', 'd': 'dual', 'p': 'plural'},
            'tense': {
                'p': 'present', 'i': 'imperfect', 'r': 'perfect', 'l': 'pluperfect',
                't': 'future perfect', 'f': 'future', 'a': 'aorist'
            },
            'mood': {
                'i': 'indicative', 's': 'subjunctive', 'o': 'optative', 'n': 'infinitive',
                'm': 'imperative', 'd': 'gerund', 'g': 'gerundive'
            },
            'voice': {'a': 'active', 'p': 'passive', 'm': 'middle', 'e': 'middle-passive'},
            'gender': {'m': 'masculine', 'f': 'feminine', 'n': 'neuter'},
            'case': {
                'n': 'nominative', 'g': 'genitive', 'd': 'dative', 'a': 'accusative',
                'v': 'vocative', 'l': 'locative'
            },
            'degree': {'c': 'comparative', 's': 'superlative'}
        }
    
    def parse_postag(self, postag: str) -> Dict[str, Optional[str]]:
        """Parse a Perseus postag string into linguistic features."""
        if len(postag) < 9:
            postag = postag.ljust(9, '-')
        
        features = {}
        mappings = [
            ('part_of_speech', 0), ('person', 1), ('number', 2), ('tense', 3),
            ('mood', 4), ('voice', 5), ('gender', 6), ('case', 7), ('degree', 8)
        ]
        
        for feature_name, index in mappings:
            char = postag[index]
            if char != '-':
                features[feature_name] = self.postag_mappings[feature_name].get(char)
            else:
                features[feature_name] = None
        
        return features
    
    def xml_to_words(self, xml_content: str) -> List[Word]:
        """Convert Perseus Treebank XML to Word objects."""
        root = ET.fromstring(xml_content)
        words = []
        
        for sentence in root.findall('.//sentence'):
            sentence_id = int(sentence.get('id'))
            
            for word_node in sentence.findall('.//word'):
                # Extract basic attributes
                lemma = word_node.get('lemma', '').replace('1', '')
                word_id = int(word_node.get('id'))
                parent_id = int(word_node.get('head', 0))
                form = word_node.get('form', '')
                relation = word_node.get('relation', '')
                postag = word_node.get('postag', '')
                
                # Parse linguistic features
                features = self.parse_postag(postag)
                
                # Create Word object
                word = Word(
                    form=form,
                    lemma=lemma,
                    id=word_id,
                    parent_id=parent_id,
                    sentence_id=sentence_id,
                    relation=relation,
                    **features
                )
                
                words.append(word)
        
        return words

class GreekQueryEngine:
    """Query engine for searching Greek texts using CSS-like selectors."""
    
    def __init__(self, words: List[Word]):
        self.words = words
        self.words_by_id = {word.id: word for word in words}
        self.words_by_sentence = {}
        
        # Group words by sentence
        for word in words:
            if word.sentence_id not in self.words_by_sentence:
                self.words_by_sentence[word.sentence_id] = []
            self.words_by_sentence[word.sentence_id].append(word)
        
        # Build parent-child relationships
        for word in words:
            if word.parent_id in self.words_by_id:
                parent = self.words_by_id[word.parent_id]
                parent.children.append(word)
    
    def query(self, selector: str) -> List[Word]:
        """Execute a query using CSS-like selector syntax."""
        # Handle comma-separated selectors
        if ',' in selector:
            results = []
            for sub_selector in selector.split(','):
                results.extend(self.query(sub_selector.strip()))
            return list(set(results))  # Remove duplicates
        
        # Handle parent-child relationships (>)
        if ' > ' in selector:
            return self._handle_parent_child(selector)
        
        # Handle adjacent words (+)
        if ' + ' in selector:
            return self._handle_adjacent(selector)
        
        # Handle word order (~)
        if ' ~ ' in selector:
            return self._handle_word_order(selector)
        
        # Handle single selector
        return self._match_single_selector(selector)
    
    def _match_single_selector(self, selector: str) -> List[Word]:
        """Match a single selector against all words."""
        results = []
        
        for word in self.words:
            if self._word_matches_selector(word, selector):
                results.append(word)
        
        return results
    
    def _word_matches_selector(self, word: Word, selector: str) -> bool:
        """Check if a word matches a selector."""
        # Handle attribute selectors [attr=value]
        attr_match = re.search(r'\[(\w+)=([^]]+)\]', selector)
        if attr_match:
            attr_name, attr_value = attr_match.groups()
            if not hasattr(word, attr_name) or getattr(word, attr_name) != attr_value:
                return False
            selector = re.sub(r'\[(\w+)=([^]]+)\]', '', selector)
        
        # Handle :root pseudo-selector
        if ':root' in selector:
            if word.parent_id != 0 or word.relation == 'AuxK':
                return False
            selector = selector.replace(':root', '')
        
        # Handle :before() and :after() pseudo-selectors
        before_match = re.search(r':before\(([^)]+)\)', selector)
        if before_match:
            inner_selector = before_match.group(1)
            if not self._check_word_order_condition(word, inner_selector, 'before'):
                return False
            selector = re.sub(r':before\([^)]+\)', '', selector)
        
        after_match = re.search(r':after\(([^)]+)\)', selector)
        if after_match:
            inner_selector = after_match.group(1)
            if not self._check_word_order_condition(word, inner_selector, 'after'):
                return False
            selector = re.sub(r':after\([^)]+\)', '', selector)
        
        # Handle linguistic pseudo-selectors
        pseudo_selectors = re.findall(r':(\w+)', selector)
        for pseudo in pseudo_selectors:
            if not self._matches_linguistic_feature(word, pseudo):
                return False
        
        # Handle lemma (direct text match)
        lemma_parts = re.sub(r':\w+|\[[^]]+\]', '', selector).strip()
        if lemma_parts:
            if word.lemma != lemma_parts:
                return False
        
        return True
    
    def _matches_linguistic_feature(self, word: Word, feature: str) -> bool:
        """Check if word matches a linguistic feature."""
        # Check all possible attributes
        attributes = [
            'part_of_speech', 'person', 'number', 'tense', 'mood', 
            'voice', 'gender', 'case', 'degree'
        ]
        
        for attr in attributes:
            if hasattr(word, attr) and getattr(word, attr) == feature:
                return True
        
        return False
    
    def _handle_parent_child(self, selector: str) -> List[Word]:
        """Handle parent > child relationships."""
        parts = selector.split(' > ')
        if len(parts) != 2:
            return []
        
        parent_selector, child_selector = parts
        parent_words = self._match_single_selector(parent_selector.strip())
        
        results = []
        for parent in parent_words:
            for child in parent.children:
                if self._word_matches_selector(child, child_selector.strip()):
                    results.append(child)
        
        return results
    
    def _handle_adjacent(self, selector: str) -> List[Word]:
        """Handle adjacent word relationships (+)."""
        parts = selector.split(' + ')
        if len(parts) < 2:
            return []
        
        results = []
        for sentence_words in self.words_by_sentence.values():
            # Sort by word ID (position in sentence)
            sentence_words.sort(key=lambda w: w.id)
            
            for i in range(len(sentence_words) - len(parts) + 1):
                match = True
                for j, part in enumerate(parts):
                    if not self._word_matches_selector(sentence_words[i + j], part.strip()):
                        match = False
                        break
                
                if match:
                    results.extend(sentence_words[i:i + len(parts)])
        
        return results
    
    def _handle_word_order(self, selector: str) -> List[Word]:
        """Handle word order relationships (~)."""
        parts = selector.split(' ~ ')
        if len(parts) != 2:
            return []
        
        first_selector, second_selector = parts
        first_words = self._match_single_selector(first_selector.strip())
        second_words = self._match_single_selector(second_selector.strip())
        
        results = []
        for first_word in first_words:
            for second_word in second_words:
                if (first_word.sentence_id == second_word.sentence_id and 
                    first_word.id < second_word.id):
                    results.append(first_word)
                    results.append(second_word)
        
        return results
    
    def _check_word_order_condition(self, word: Word, selector: str, direction: str) -> bool:
        """Check word order conditions for :before() and :after()."""
        target_words = []
        
        # Find words in the same sentence that match the selector
        sentence_words = self.words_by_sentence.get(word.sentence_id, [])
        for w in sentence_words:
            if self._word_matches_selector(w, selector):
                target_words.append(w)
        
        # Check if any target words are in the correct direction
        for target in target_words:
            if direction == 'before' and word.id < target.id:
                return True
            elif direction == 'after' and word.id > target.id:
                return True
        
        return False

def create_query_engine(xml_content: str) -> GreekQueryEngine:
    """Create a query engine from Perseus Treebank XML."""
    parser = GreekTextParser()
    words = parser.xml_to_words(xml_content)
    return GreekQueryEngine(words)