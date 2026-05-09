import pandas as pd

grammar = pd.read_csv("data/grammar.csv")
vocab = pd.read_csv("data/vocab.csv")
reading = pd.read_csv("data/reading_questions.csv")

print("\nGRAMMAR:")
print(grammar.head())

print("\nVOCAB:")
print(vocab.head())

print("\nREADING:")
print(reading.head())