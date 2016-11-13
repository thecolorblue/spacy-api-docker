import spacy
from flask_restful import reqparse, Resource

# make queries against Neo4j
# queries must have two of the three parts saved to the db
# (1. Noun)<-[:SUBJECT]-(2. VERB)-[:OBJECT]->(3. Noun)
# /query?subject=&verb=
# /query?subject=&object=
# /query?object=&verb=

parser = reqparse.RequestParser()
parser.add_argument('subject', type=str, location='args')
parser.add_argument('object', type=str, location='args')
parser.add_argument('verb', type=str, location='args')

from neo4j.v1 import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687")
session = driver.session()

class Query(Resource):

    def get(self):
        args = parser.parse_args()

        validation = self.__validate_input(args)
        if validation:
            return validation, 500

        # make request to neo4j for missing argument
        try:
            ret = session.run('MATCH paths = (:Noun { text: {subject} })-[:SUBJECT]->(:Verb { text: { text: {verb}} })-[:OBJECT]->(:Noun { text: {object} }) return paths', args)
            return ret, 200
        except Error:
            return Error, 400

    def post(self):
        return 400

    @staticmethod
    def __validate_input(args: dict):
        if (not args.get('verb') and not args.get('object')) or (not args.get('subject') and not args.get('object')) or (not args.get('verb') and not args.get('subject')):
            return {
               'message': 'missing argument',
               'error': True
           }

        return None

    @staticmethod
    def __analyze(text: str, fields: list):
        doc = nlp(text)

        ret = {
            'numOfSentences': len(list(doc.sents)),
            'numOfTokens': len(list(doc)),
            'sentences': []
        }

        # turn this into a view layer that can be customized
        # add any helper functions into a model layer
        # (Noun)<-[:SUBJECT]-(VERB)-[:OBJECT]->(Noun)
        for sentence in doc.sents:
            sentence_analysis = [{
                'token': w.orth_,
                'lemma': w.lemma_,
                'tag': w.tag_,
                'ner': w.ent_type_,
                'offsets': {
                    'begin': w.idx,
                    'end': w.idx + len(w.orth_)
                },
                'oov': w.is_oov,
                'stop': w.is_stop,
                'url': w.like_url,
                'email': w.like_email,
                'num': w.like_num,
                'pos': w.pos_,
                'dep': w.dep_,
                'target': w.head.text
            } for w in sentence]

            if fields:
                # Remove certain fields if requested
                sentence_analysis = [
                    dict([(k, v) for k, v in token.items() if k in fields])
                    for token in sentence_analysis
                ]
            ret['sentences'].append(sentence_analysis)
        return ret
