from similar_closed_incident_mock import SampleMock
from DemistoMock.utilities import register_module_line, __line__, return_error, is_error, get_error
import timedelta
from DemistoMock.markdown import formats, entryTypes, tableToMarkdown

demisto = SampleMock()

import json
import sys
import dateutil.parser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from six import string_types
register_module_line('SimilarClosedIncident', 'start', __line__())


INCIDENT_TEXT_FIELD = 'incident_text_for_tfidf'
CLASSIFICATION_FIELD = 'phishingclassification'
MATCH_THRESHOLD = 60


def parse_datetime(datetime_str):
    return dateutil.parser.parse(datetime_str)


def get_similar_texts(text, other_texts):
    vect = TfidfVectorizer(min_df=1, stop_words='english')
    if type(text) is not list:
        text = [text]
    tfidf = vect.fit_transform(text + list(other_texts))
    similarity_vector = linear_kernel(tfidf[0:1], tfidf).flatten()
    return similarity_vector[1:]


def get_texts_from_incident(incident, text_fields):
    texts = []
    # labels
    for label in incident.get('labels') or []:
        if label['type'].lower() in text_fields:
            texts.append(label['value'])

    # custom fields + incident fields.
    custom_fields = incident.get('CustomFields') or {}
    for field_name, field_value in (list(custom_fields.items()) + list(incident.items())):
        if field_name in text_fields and isinstance(field_value, string_types):
            texts.append(field_value)

    return " ".join(texts)


def add_text_to_incident(incident, text_fields):
    incident[INCIDENT_TEXT_FIELD] = get_texts_from_incident(incident, text_fields)


def get_incidents_by_time(incident_time, incident_type, incident_id, hours_time_frame,
                          max_number_of_results, time_field):
    incident_time = parse_datetime(incident_time)
    max_date = incident_time + timedelta(hours=hours_time_frame)
    min_date = incident_time - timedelta(hours=hours_time_frame)
    query = '{0}:>="{1}" and {0}:<="{2}" and type:"{3}"'.format(time_field, min_date.isoformat(), max_date.isoformat(),
                                                                incident_type)
    query += " and status: closed"

    if incident_id:
        query += ' and -id:%s' % incident_id

    query += ' and -{0}:UNKNOWN'.format(CLASSIFICATION_FIELD)

    args = {'query': query, 'size': max_number_of_results, 'sort': '%s.desc' % time_field}
    if time_field == "created":
        args['from'] = min_date.isoformat()

    res = demisto.executeCommand('GetIncidentsByQuery', {
        'query': query,
        'fromDate': min_date.isoformat(),
        'toDate': max_date.isoformat(),
        'limit': max_number_of_results
    })
    if is_error(res):
        return_error(res)

    incident_list = json.loads(res[0]['Contents']) if len(res) > 0 else []
    return incident_list


def incident_to_record(incident, time_field):
    def parse_time(date_time_str):
        try:
            if date_time_str.find('.') > 0:
                date_time_str = date_time_str[:date_time_str.find('.')]
            if date_time_str.find('+') > 0:
                date_time_str = date_time_str[:date_time_str.find('+')]
            return date_time_str.replace('T', ' ')
        except Exception:
            return date_time_str

    occured_time = parse_time(incident[time_field])
    return {'id': incident['id'],
            'phishingclassification': incident[CLASSIFICATION_FIELD],
            'name': incident['name'],
            'status': incident['status'],
            'closedTime': parse_time(incident['closed']) if incident['closed'] != "0001-01-01T00:00:00Z" else "",
            'Time': occured_time,
            'similarity': "{0:.2f}".format(incident['similarity'])
            }


def pre_process_nlp(text_data):
    res = demisto.executeCommand('WordTokenizerNLP', {
        'value': json.dumps(text_data),
        'isValueJson': 'yes',
    })
    if is_error(res):
        return_error(get_error(res))
    processed_text_data = res[0]['Contents']
    if not isinstance(processed_text_data, list):
        processed_text_data = [processed_text_data]
    tokenized_text_data = map(lambda x: x.get('tokenizedText'), processed_text_data)
    return tokenized_text_data



# get all incidents that match
def getIncidents(incident):
    TEXT_FIELDS = set(map(lambda x: x.lower(), demisto.args()['textFields'].split(',')))
    MIN_TEXT_LENGTH = int(demisto.args()['minTextLength'])
    TIME_FIELD = demisto.args()['timeField']
    HOURS_TIME_FRAME = float(demisto.args()['timeFrameHours'])
    PRE_PROCESS_TEXT = demisto.args()['preProcessText'] == 'true'
    INCIDENT_QUERY_SIZE = int(demisto.args()['maximumNumberOfIncidents'])

    incident_text = get_texts_from_incident(incident, TEXT_FIELDS)

    if len(incident_text) < MIN_TEXT_LENGTH:
        demisto.results("The text is too short to compare - minimum of %d chars required" % MIN_TEXT_LENGTH)
        sys.exit(0)

    # get initial candidates list
    candidates = get_incidents_by_time(incident[TIME_FIELD], incident['type'], incident['id'], HOURS_TIME_FRAME,
                                       INCIDENT_QUERY_SIZE, TIME_FIELD)

    # filter candidates with minimum length constraint
    for candidate in candidates:
        add_text_to_incident(candidate, TEXT_FIELDS)

    map(lambda x: add_text_to_incident(x, TEXT_FIELDS), candidates)
    candidates = [x for x in candidates if len(x.get(INCIDENT_TEXT_FIELD, "")) >= MIN_TEXT_LENGTH]

    # compare candidates to the orginial incident using TF-IDF
    candidates_text = map(lambda x: x[INCIDENT_TEXT_FIELD], candidates)
    if PRE_PROCESS_TEXT:
        incident_text = pre_process_nlp(incident_text)
        candidates_text = pre_process_nlp(candidates_text)

    similarity_vector = get_similar_texts(incident_text, candidates_text)
    similar_incidents = []
    for (i, similarity) in enumerate(similarity_vector):
        candidates[i]['similarity'] = similarity
        if similarity >= MATCH_THRESHOLD:
            similar_incidents.append(candidates[i])   

    return similar_incidents

def main():
    MAX_CANDIDATES_IN_LIST = int(demisto.args()['maxResults'])
    TIME_FIELD = demisto.args()['timeField']
    THRESHOLD = float(demisto.args()['threshold'])
    isSimilarIncidentFound = False
    similarIncident = None

    incident = demisto.incidents()[0]

    similar_incidents = getIncidents(incident)
 
    # update context
    if len(similar_incidents or []) > 0:
        similar_incidents_rows = map(lambda incident: incident_to_record(incident, TIME_FIELD), similar_incidents)
        similar_incidents_rows = sorted(similar_incidents_rows, key=lambda x: [x['similarity'], x['Time']], reverse=True)

        for r in similar_incidents_rows:
            if r["similarity"] >= THRESHOLD:
                similarIncident = r
                isSimilarIncidentFound = True

        context = {
            'similarIncidentList': similar_incidents_rows[:MAX_CANDIDATES_IN_LIST],
            'similarIncident': similarIncident,
            'isSimilarIncidentFound': isSimilarIncidentFound
        }
        markdown_result = tableToMarkdown("Similar incidents",
                                          similar_incidents_rows,
                                          headers=['id', 'name', 'closedTime', 'Time', 'similarity', 'phishingclassification'])
        return {'ContentsFormat': formats['markdown'],
                'Type': entryTypes['note'],
                'Contents': markdown_result,
                'EntryContext': context}

    else:
        context = {
            'isSimilarIncidentFound': False
        }
        return {'ContentsFormat': formats['markdown'],
                'Type': entryTypes['note'],
                'Contents': 'No similar incidents has been found',
                'EntryContext': context}


if __name__ in ['__main__', '__builtin__', 'builtins']:
    main()

register_module_line('SimilarClosedIncident', 'end', __line__())
