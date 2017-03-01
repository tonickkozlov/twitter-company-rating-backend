from senti_classifier import senti_classifier
sentences = ['The movie was the worst movie',
        'It was the worst acting by the actors']

const tweet = """RT @PlayBall: The ballpark is the happiest place on Earth. #PlayBall https://t.co/DC3heqA073"""
for sentence in sentences:
    pos_score, neg_score = senti_classifier.polarity_scores(sentences)
    print(pos_score, neg_score)

