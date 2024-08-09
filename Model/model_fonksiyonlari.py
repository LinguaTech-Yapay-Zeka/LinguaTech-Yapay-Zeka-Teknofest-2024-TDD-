import tensorflow as tf
from tf_keras.preprocessing.text import tokenizer_from_json
from transformers import pipeline ,AutoModelForTokenClassification ,AutoTokenizer
import spacy
import numpy as np
import pickle
from collections import defaultdict

loaded_model = AutoModelForTokenClassification.from_pretrained("saved_model")
loaded_tokenizer = AutoTokenizer.from_pretrained("saved_model")
ner_pipeline = pipeline("ner", model=loaded_model, tokenizer=loaded_tokenizer,device=-1)

def entitylist(text):
    results = ner_pipeline(text)
    combined_results = []
    current_word = ''
    current_entity = ''
    current_start = None
    last_end = 0
    for item in results:
        word = item['word']
        entity = item['entity']
        start = item['start']
        end = item['end']
        if word.startswith('##'):
            current_word += word[2:]
            last_end = end
        else:
            if current_word:
               combined_results.append({
                    'entity': current_entity,
                    'word': current_word,
                    'start': current_start,
                    'end': last_end
                })
            current_word = word
            current_entity = entity
            current_start = start
            last_end = end
    if current_word:
        combined_results.append({
            'entity': current_entity,
            'word': current_word,
            'start': current_start,
            'end': last_end
        })
    final_results = []
    buffer = None
    for item in combined_results:
        if item['entity'] == 'B-ORG':
            if buffer:
                buffer['word'] += ' ' + item['word']
                buffer['end'] = item['end']
                final_results.append(buffer)
                buffer = None
            else:
                final_results.append(item)
        elif item['entity'] == 'I-ORG':
            if final_results and final_results[-1]['entity'] == 'B-ORG':
                final_results[-1]['word'] += ' ' + item['word']
                final_results[-1]['end'] = item['end']
            else:
                final_results.append(item)
        else:
            if buffer:
                final_results.append(buffer)
                buffer = None
            final_results.append(item)
    if buffer:
        final_results.append(buffer)
    entity_list = []
    for item in final_results:
        entity_list.append(text[item['start']:item['end']])
    return entity_list


def phrase_separator(entity_phrases):
    new_dict = defaultdict(list)
    for key, value in entity_phrases.items():
        new_list = []
        for phrase in value:
            new_list.append(phrase)
            if len(phrase.split(' ')) >= 3:
                string = ' '.join(new_list)
                new_dict[key].append(string)
                new_list = []

        if len(new_list) > 0:
            string = ' '.join(new_list)
            new_dict[key].append(string)
    return new_dict

nlp = spacy.load('tr_core_news_trf')


def get_entity_phrases(text, entities):
    doc = nlp(text)
    entity_phrases = defaultdict(list)
    entity_positions = {}
    for entity in entities:
        start = doc.text.find(entity)
        if start != -1:
            end = start + len(entity)
            entity_positions[entity] = (start, end)

    segments = doc.text.split(',')
    for i, segment in enumerate(segments):
        segment_doc = nlp(segment.strip())


        segment_entities = [e for e, (start, end) in entity_positions.items() if start <= doc.text.index(segment) < end]

        for token in segment_doc:
            if token.pos_ in ["ADJ", "ADV", "VERB"]:
                phrase = [token.text]
                for child in token.children:
                    if child.pos_ == "ADV" and child.dep_ == "advmod":
                        phrase.insert(0, child.text)
                    elif child.pos_ == "NOUN" and child.dep_ in ["nsubj", "obj", "obl"]:
                        phrase.append(child.text)
                phrase_text = ' '.join(phrase)


                if segment_entities:
                    assigned_entity = segment_entities[0]
                else:

                    token_position = doc.text.index(segment) + token.idx
                    assigned_entity = min(entity_positions.items(), key=lambda x: min(abs(token_position - x[1][0]),
                                                                                      abs(token_position - x[1][1])))[0]

                entity_phrases[assigned_entity].append(phrase_text)


    result = {entity: phrases for entity, phrases in entity_phrases.items()}
    result = phrase_separator(result)


    for entity in entities:
        if entity not in result:
            result[entity] = []

    return result

model = tf.saved_model.load('sentimentmodel')

with open('tokenizer.pkl', 'rb') as file:
    tokenizer_json = pickle.load(file)

tokenizer = tokenizer_from_json(tokenizer_json)

def predict_sentiment(text):


    sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = tf.keras.preprocessing.sequence.pad_sequences(sequence, maxlen=100)


    padded_sequence = tf.cast(padded_sequence, tf.float32)


    with tf.device('/GPU:0'):
        prediction = model(padded_sequence, training=False)


    if isinstance(prediction, tf.Tensor):
        prediction = prediction.numpy()


    sentiment_labels = ['olumlu', 'nötr', 'olumsuz']
    sentiment_index = np.argmax(prediction[0])
    predicted_sentiment = sentiment_labels[sentiment_index]

    return predicted_sentiment, prediction[0]


def entity_phrases_sentiment(entityler, entity_phrases):
    results = []
    for entity in entityler:
        if entity in entity_phrases:
            sentiments = []
            for phrase in entity_phrases[entity]:
                sentiment, scores = predict_sentiment(phrase)
                sentiments.append(sentiment)

            if len(sentiments) > 1:
                for unique_sentiment in set(sentiments):
                    results.append({"entity": entity, "sentiment": unique_sentiment})
            else:

                results.append({"entity": entity, "sentiment": sentiments[0] if sentiments else 'nötr'})
        else:

            results.append({"entity": entity, "sentiment": 'nötr'})
    return results

def calistir(text):
    entityler = entitylist(text)

    entity_phrases = get_entity_phrases(text, entityler)

    results = entity_phrases_sentiment(entityler, entity_phrases)

    entity_list = entityler
    result = {
        "entity_list": entity_list,
        "results": results
    }
    return result