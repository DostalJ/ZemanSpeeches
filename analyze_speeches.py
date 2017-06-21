from pandas import read_csv
from nltk.tokenize import word_tokenize
import nltk
from czech_stemmer_rev0.czech_stemmer import cz_stem
from nltk.stem import PorterStemmer


cz_words = ['čína', 'trump', 'putin', 'česko', 'eu', 'evropa', 'evropska', 'uprchlíci', 'islám', 'hranice', 'zeď', 'skvělé', 'národ', 'německo', 'terorismus']
en_words = ['china', 'trump', 'putin', 'czech', 'eu', 'europe', 'european', 'refugee', 'islam', 'borders', 'wall', 'great', 'nation', 'germany', 'terrorism']

print('-'*40)
df1 = read_csv(filepath_or_buffer='./Zeman/speeches.csv', sep=';')
text = ' '.join(df1['text'].values.tolist())
tokenized_text = [w.lower() for w in word_tokenize(text)]
stemmed_text = [cz_stem(w) for w in tokenized_text]
for w in cz_words:
    print('Occurrences of {:s}: {:f}'.format(
        w, 100000 * stemmed_text.count(cz_stem(w)) / len(stemmed_text)))

print('-'*40)
df2 = read_csv(filepath_or_buffer='./Trump/speeches.csv', sep=';')
df2 = df2.dropna(0, 'any')
text = ' '.join(df2['text'].values.tolist())
tokenized_text = [w.lower() for w in word_tokenize(text)]
ps = PorterStemmer()
stemmed_text = [ps.stem(w) for w in tokenized_text]
for w in en_words:
    print('Occurrences of {:s}: {:f}'.format(
        w, 100000 * stemmed_text.count(ps.stem(w)) / len(stemmed_text)))
