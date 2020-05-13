import numpy as np
import pytest

from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa.nlu.tokenizers.tokenizer import Tokenizer
from rasa.nlu.training_data import TrainingData
from rasa.nlu.constants import TEXT, TOKENS_NAMES, RESPONSE, INTENT
from rasa.nlu.training_data import Message
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.featurizers.dense_featurizer.convert_featurizer import ConveRTFeaturizer


def test_convert_featurizer_process():
    featurizer = ConveRTFeaturizer.create({}, RasaNLUModelConfig())

    sentence = "Hey how are you today ?"
    message = Message(sentence)
    tokens = WhitespaceTokenizer().tokenize(message, attribute=TEXT)
    tokens = Tokenizer.add_cls_token(tokens, attribute=TEXT)
    message.set(TOKENS_NAMES[TEXT], tokens)

    featurizer.process(message)

    expected = np.array([2.2636216, -0.26475656, -1.1358104, -0.49751878, -1.3946456])
    expected_cls = np.array(
        [1.0251294, -0.04053932, -0.7018805, -0.82054937, -0.75054353]
    )

    seq_vecs, sent_vecs = message.get_dense_features(TEXT, [], [])

    assert len(tokens) == len(seq_vecs) + len(sent_vecs)
    assert np.allclose(seq_vecs[0][:5], expected, atol=1e-5)
    assert np.allclose(sent_vecs[-1][:5], expected_cls, atol=1e-5)


def test_convert_featurizer_train():
    featurizer = ConveRTFeaturizer.create({}, RasaNLUModelConfig())

    sentence = "Hey how are you today ?"
    message = Message(sentence)
    message.set(RESPONSE, sentence)
    tokens = WhitespaceTokenizer().tokenize(message, attribute=TEXT)
    tokens = Tokenizer.add_cls_token(tokens, attribute=TEXT)
    message.set(TOKENS_NAMES[TEXT], tokens)
    message.set(TOKENS_NAMES[RESPONSE], tokens)

    featurizer.train(TrainingData([message]), RasaNLUModelConfig())

    expected = np.array([2.2636216, -0.26475656, -1.1358104, -0.49751878, -1.3946456])
    expected_cls = np.array(
        [1.0251294, -0.04053932, -0.7018805, -0.82054937, -0.75054353]
    )

    seq_vecs, sent_vecs = message.get_dense_features(TEXT, [], [])

    assert len(tokens) == len(seq_vecs) + len(sent_vecs)
    assert np.allclose(seq_vecs[0][:5], expected, atol=1e-5)
    assert np.allclose(sent_vecs[-1][:5], expected_cls, atol=1e-5)

    seq_vecs, sent_vecs = message.get_dense_features(RESPONSE, [], [])

    assert len(tokens) == len(seq_vecs) + len(sent_vecs)
    assert np.allclose(seq_vecs[0][:5], expected, atol=1e-5)
    assert np.allclose(sent_vecs[-1][:5], expected_cls, atol=1e-5)

    seq_vecs, sent_vecs = message.get_dense_features(INTENT, [], [])

    assert seq_vecs is None
    assert sent_vecs is None


@pytest.mark.parametrize(
    "sentence, expected_text",
    [
        ("hello", "hello"),
        ("you're", "you re"),
        ("r. n. b.", "r n b"),
        ("rock & roll", "rock & roll"),
        ("ńöñàśçií", "ńöñàśçií"),
    ],
)
def test_convert_featurizer_tokens_to_text(sentence, expected_text):
    tokens = WhitespaceTokenizer().tokenize(Message(sentence), attribute=TEXT)

    actual_text = ConveRTFeaturizer._tokens_to_text([tokens])[0]

    assert expected_text == actual_text
