import spacy
from flask_restful import reqparse, Resource

# parse text and then save to neo4j
# queries must have two of the three parts saved to the db
# (1. Noun)<-[:SUBJECT]-(2. VERB)-[:OBJECT]->(3. Noun)
# /query?subject=&verb=
# /query?subject=&object=
# /query?object=&verb=

parser = reqparse.RequestParser()
parser.add_argument('text', type=str, location='json')

language = os.environ['LANG'] or 'en'

print("Loading Language Model for '%s'..." % language)
nlp = spacy.load(language)
print("Language Model for '%s' loaded!" % language)


class Spacy(Resource):

    def get(self):
        return 200

    def post(self):
        t0 = time.time()
        args = parser.parse_args()

        validation = self.__validate_input(args)
        if validation:
            return validation, 500

        ret = {
            'version': '1.2.0',
            'lang': language
        }

        if args.get('text'):
            # Analyze only a single text
            ret.update(
                self.__analyze(args.get('text'), args.get('fields')))
        elif args.get('texts'):
            ret['texts'] = [
                self.__analyze(text, args.get('fields'))
                for text in args.get('texts')]
            ret['numOfTexts'] = len(args.get('texts'))

        ret['performance'] = time.time() - t0,
        ret['error'] = False
        return ret, 200

    @staticmethod
    def __validate_input(args: dict):
        message = ""
        if not args.get('text') and not args.get('texts'):
            message = "No text(s) received."
        if args.get('texts') and not isinstance(args.get('texts'), list):
            message = 'Wrong format for "texts". A list of strings is required.',
        if message:
            return {
               'message': message,
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
