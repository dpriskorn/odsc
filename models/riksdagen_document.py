import logging
from typing import List

import spacy
from bs4 import BeautifulSoup
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RiksdagenDocument(BaseModel):
    """This model supports extraction of sentences based on html or text input
    It uses spaCy to find sentence boundaries"""

    id: str
    text: str = ""
    html: str = ""
    chunk_size: int = 100000
    chunks: List[str] = list()
    sentences: List[str] = list()
    token_count: int = 0

    @property
    def count_words(self) -> int:
        # Counting words in the text
        return len(self.text.split())

    @property
    def number_of_chunks(self) -> int:
        # Count the number of chunks
        return len(self.chunks)

    @property
    def number_of_sentences(self) -> int:
        # Count the number of chunks
        return len(self.sentences)

    def chunk_text(self):
        # Function to chunk the text
        start = 0
        while start < len(self.text):
            self.chunks.append(self.text[start : start + self.chunk_size])
            start += self.chunk_size

    def convert_html_to_text(self):
        # Check if HTML content exists for the document
        soup = BeautifulSoup(self.html, "lxml")
        # Extract text from the HTML
        # TODO investigate how stripping affects the result
        self.text = soup.get_text(separator=" ", strip=False)

    def extract_sentences(self):
        if not self.text:
            # We assume html is present
            self.convert_html_to_text()
        # Load the Swedish language model
        nlp = spacy.load("sv_core_news_sm")

        # Displaying the word count
        logger.info(f"Number of words before tokenization: {self.count_words}")

        # Chunk the text
        self.chunk_text()

        # Display the number of chunks
        logger.info(f"Number of chunks: {self.number_of_chunks}")

        # Process each chunk separately
        count = 1
        for chunk in self.chunks:
            logger.info(f"loading chunk {count}/{self.number_of_chunks}")
            doc = nlp(chunk)

            # Filter out sentences consisting only of newline characters
            filtered_sentences = [sent.text for sent in doc.sents if sent.text.strip()]
            self.sentences.extend(filtered_sentences)

            # Count tokens in each sentence
            for sent in filtered_sentences:
                sent_doc = nlp(sent)
                self.token_count += len(sent_doc)

            count += 1

        logger.info(f"Extracted {len(self.sentences)} sentences")
