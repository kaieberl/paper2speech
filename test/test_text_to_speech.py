import unittest
from unittest.mock import patch

from src import MarkdownModel


class TestMarkdownModel(unittest.TestCase):
    def setUp(self):
        self.markdown_model = MarkdownModel()

    @patch('subprocess.run')
    def test_heading(self, mock_subprocess):
        mock_subprocess.return_value = 'True'
        test_input = """# Graph Element Networks: adaptive, structured computation and memory

Ferran Alet\({}^{\,1}\)  Adarsh K. Jeewajee\({}^{\,1}\)  Maria Bauza\({}^{\,2}\)

**Alberto Rodriguez\({}^{\,2}\)  Tomas Lozano-Perez\({}^{\,1}\)  Leslie Pack Kaelbling\({}^{\,1}\)**"""
        self.markdown_model.markdown_to_html(test_input)
        expected_output = """<break time="0.5s"/><p>Graph Element Networks: adaptive, structured computation and memory</p><break time="0.5s"/><p>Ferran Alet,1  Adarsh K. Jeewajee,1  Maria Bauza,2</p><p><emphasis>Alberto Rodriguez,2  Tomas Lozano-Perez,1  Leslie Pack Kaelbling,1</emphasis></p>"""
        self.assertEqual(self.markdown_model.ssml.strip(), expected_output)

    def test_math_equations(self):
        test_input = "latent function over the space \(\mathbb{X}\) as \(z(x)=\sum_{l}r(x)_{l}z_{l}^{T}\)"
        self.markdown_model.markdown_to_html(test_input)
        expected_output = '<p>latent function over the space X as z(x)= summation over l r(x) l z l transpose</p>'
        self.assertEqual(self.markdown_model.ssml.strip(), expected_output)

    def test_citations(self):
        test_input = "We use neural processes (NPs) (Garnelo et al., 2018), which were also used by Eslami et al. (2018)."
        self.markdown_model.markdown_to_html(test_input)
        expected_output = "<p>We use neural processes (NPs), which were also used by Eslami et al.</p>"
        self.assertEqual(self.markdown_model.ssml.strip(), expected_output)

    def test_list(self):
        test_input = """* Any point inside the house follows the Laplace equation;
* Any point in a heater or cooler follows the Poisson equation;
* All exterior borders are modeled as very thin windows"""
        self.markdown_model.markdown_to_html(test_input)
        expected_output = """<p>Any point inside the house follows the Laplace equation;</p><p>Any point in a heater or cooler follows the Poisson equation;</p><p>All exterior borders are modeled as very thin windows</p>"""
        self.assertEqual(self.markdown_model.ssml.strip(), expected_output)

    def test_url(self):
        test_input = "Code can be found at [https://github.com/FerranAlet/graph_element_networks](https://github.com/FerranAlet/graph_element_networks)."
        self.markdown_model.markdown_to_html(test_input)
        expected_output = "<p>Code can be found at.</p>"
        self.assertEqual(self.markdown_model.ssml.strip(), expected_output)

    def test_authors(self):
        test_input = """# Graph Element Networks: adaptive, structured computation and memory

Ferran Alet\({}^{\,1}\)  Adarsh K. Jeewajee\({}^{\,1}\)  Maria Bauza\({}^{\,2}\)

**Alberto Rodriguez\({}^{\,2}\)  Tomas Lozano-Perez\({}^{\,1}\)  Leslie Pack Kaelbling\({}^{\,1}\)**

###### Abstract"""
        self.markdown_model.markdown_to_html(test_input)
        expected_output = '<break time="0.5s"/><p>Graph Element Networks: adaptive, structured computation and memory</p><break time="0.5s"/><break time="0.5s"/><p>Abstract</p><break time="0.5s"/>'
        self.assertEqual(self.markdown_model.ssml.strip(), expected_output)


# for debugging
def run_text_to_speech(ssml):
    import os
    from google.cloud import texttospeech

    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PROJECT_DIR, "../src/texttospeech.json")

    speech_client = texttospeech.TextToSpeechClient()

    ssml = "<speak>\n" + ssml + "</speak>\n"
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-GB',
        name='en-GB-Wavenet-B',
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    # generate speech
    response = speech_client.synthesize_speech(
        request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
    )
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
