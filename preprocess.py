import os
import numpy as np
import pandas as pd

from collections import Counter

class PreprocessData:
    def __init__(self, root_dir, seq_len=32, batch_size=16):
        self.root_dir = root_dir
        self.seq_len = seq_len
        self.batch_size = batch_size

        self.load_files()
        self.build_vocab()

    def load_files(self):
        filenames = os.listdir(self.root_dir)
        self.stories = []
        for filename in filenames:
            story = self.load_file(filename)
            self.stories.append(story)

    def load_file(self, filename):
        file_path = os.path.join(self.root_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            story = f.read().lower()
        return story

    def save_to_df(self, output_path):
        X, y = [], []
        for story in self.stories:
            story_X, story_y = self.process_story(story)
            X.append(story_X)
            y.append(story_y)
        
        df = pd.DataFrame({"X": X, "y": y})
        df.to_csv(output_path, index=False)

    def build_vocab(self):
        word_counts = Counter()
        for story in self.stories:
            word_counts.update(story.split())
        sorted_vocab = sorted(word_counts, key=word_counts.get, reverse=True)
        self.int2vocab = {k: w for k, w in enumerate(sorted_vocab)}
        self.vocab2int = {w: k for k, w in self.int2vocab.items()}

    def process_story(self, story):
        int_text = [self.vocab2int[w] for w in story.split()]
        num_batches = int(len(int_text) / (self.seq_len * self.batch_size))

        in_text = int_text[:num_batches * self.batch_size * self.seq_len]
        out_text = np.zeros_like(in_text)
        out_text[:-1] = in_text[1:]
        out_text[-1] = in_text[0]

        return in_text, out_text
    
preprocesser = PreprocessData("fanfics")
preprocesser.save_to_df("processed.csv")
