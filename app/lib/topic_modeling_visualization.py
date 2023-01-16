import os

import spacy

nlp = spacy.load('en_core_web_sm')

import pickle
import numpy as np
import pandas as pd
import emoji
import scattertext as st
from gsdmm import MovieGroupProcess

from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.models.phrases import Phrases
from gensim.parsing.preprocessing import preprocess_string, STOPWORDS
from gensim.parsing.preprocessing import strip_tags, strip_punctuation, strip_multiple_whitespaces, strip_numeric, \
    strip_short


class TweetTextData():
    def __init__(self, trunc_data_length: int = 30000,
                 load_labeled_data: bool = True,
                 raw_data_path: str = "../data/social_media_data/tweet_search_data",
                 labeled_data_pickle="../data/social_media_data/cleaned_tweets/labeled_tweets.pickle",
                 read_from_disk: bool = True,
                 spacy_lemmas: bool = True,
                 gdrive_file_path=False
                 ):
        """
            This is creates a TweetTextData object. It expects the data path to contain CSV files with same columns od date, text, userid, likeCount, replyCount, retweetCount, coordinates, hashtags
            :param trunc_data_length:  Set the length of a truncated dataframe. THIS DOES NOT TRUNCATE THE DATAFRAME, It is used in conjunction with the trunc_df flag in functions that can take a long time to run
            :param load_labeled_data:  Unsupervised learning assigned labels are stored in a pickle file. If this is set all cleaning, processing and unsupervised learning is circumvented and the dataset with unsupervised learning data is loaded
            :param raw_data_path: The default path for Tweet text is in the parameter: "../data/social_media_data/tweet_search_data/"
            :param spacy_lemmas:bool=True, This variable if true is used to determine if we are using cleaned tokens that as Spacy lemmas or gensim tokens
            :param read_from_disk: If cleaning, lemmatization and tokenization has been performed then this data has been stored on the disk and so pick it up from there
            :param gdrive_file_path: Set this if working in Google Colab


        """
        if gdrive_file_path:
            raw_data_path = '/content/drive/MyDrive/Capstone/data/social_media_data/tweet_search_data'

        self.CUSTOM_STOP_WORDS = ['www', 'tinyurl', 'com', 'https', 'http', '&amp', 'rt', 'bit', 'ly', 'bitly', 'shit']
        self.CUSTOM_FILTERS = [lambda x: x.lower(), strip_tags, strip_punctuation, strip_multiple_whitespaces,
                               strip_numeric, strip_short]

        if gdrive_file_path:
            self.lda_model_saved_path = '/content/drive/MyDrive/Capstone/data/social_media_data/models/lda_models/'
            self.gdsmm_model_saved_path = '/content/drive/MyDrive/Capstone/data/social_media_data/models/gdsmm_models/'
        else:
            self.lda_model_saved_path = '../data/social_media_data/models/lda_models/'
            self.gdsmm_model_saved_path = '../data/social_media_data/models/gdsmm_models/'

        if not gdrive_file_path:
          self.labeled_data_pickle = labeled_data_pickle
        else:
          self.labeled_data_pickle = "/content/drive/MyDrive/Capstone/data/social_media_data/cleaned_tweets/labeled_tweets.pickle"


        self.read_from_disk = read_from_disk
        self.gdrive_file_path = gdrive_file_path
        self.spacy_lemmas = spacy_lemmas

        if load_labeled_data:
            
              # Data has been cleaned, lemmatized and a GSDMM model has been applied to get the unsupervised learning labels
              self.tweet_df = pd.read_pickle(self.labeled_data_pickle)
        else:
            # If read_from_disk is set the data has been cleaned and lemmatized and stored in pickle file
            if read_from_disk:
                if gdrive_file_path:
                    cleaned_file_path = "/content/drive/MyDrive/Capstone/data/social_media_data/cleaned_tweets/cleaned_lemmatized_tweets.pickle"
                else:
                    cleaned_file_path = "../data/social_media_data/cleaned_tweets/cleaned_lemmatized_tweets.pickle"
                self.tweet_df = pd.read_pickle(cleaned_file_path)
            else:
                # Start from scratch
                self.tweet_df = pd.DataFrame()
                for file_name in os.listdir(raw_data_path):
                    full_path = os.path.join(raw_data_path, file_name)
                    df = pd.read_csv(full_path)
                    self.tweet_df = pd.concat([self.tweet_df, df], axis='rows')
                    # Drop duplicates of all the fields we are keeping in the dataset
                    self.tweet_df.drop_duplicates(inplace=True)

        self.trunc_data_length = trunc_data_length
        print(f"Dataframe has a shape of : {self.tweet_df.shape}")

    # from SIADS 682
    def post_process_stopwords(self, token_list):
        if len(token_list) == 0:
            new_list = []
        else:
            new_list = [token for token in token_list if token not in self.CUSTOM_STOP_WORDS and token not in STOPWORDS]

        return new_list

    # From SIADS 622some utility classes that will help us load the data in
    def lemmatize(self, instring, title="", lemmaCache={}):
        parsed = None

        if ((title != "") & (title in lemmaCache)):
            parsed = lemmaCache[title]
        else:
            parsed = nlp(instring)

        if (lemmaCache != None):
            lemmaCache[title] = parsed
        sent = [x.text if (x.lemma_ == "-PRON-") else x.lemma_ for x in parsed]
        return (sent)

    def partial_preprocess(self, text):
        new_str = emoji.replace_emoji(text, " ")
        new_str = " ".join(preprocess_string(new_str, self.CUSTOM_FILTERS))
        new_str = self.lemmatize(new_str)
        return new_str

    def clean_tokenize_text(self, trunc_df: bool = False):
        """
            A function that cleans and tokenizes the text in the column 'text' and saves it in a column called 'tokens'.
            These are the changes we'll see performed on the original 'text':
            - remove tags
            - strip punctuation
            - remove multiple whitespace
            - remove numeric characters
            - tokenize words
            - return a lower-case stemmed version of the text
            - remove common STOPWORDS (imported from gensim's Stone, Denis, Kwantes (2010) dataset)
            - remove CUSTOM_STOP_WORDS, defined above

        """
        if trunc_df:
            self.tweet_df = self.tweet_df.iloc[:self.trunc_data_length, :].copy()

        self.tweet_df['text'] = self.tweet_df['text'].astype(str)
        # # remove profanity: this slows things considerably and so commenting Out
        # self.tweet_df['text'] = self.tweet_df['text'].apply(lambda text: profanity.censor(text))
        # #Use Gensim's preprocess but lemmatize instead of Stem using Spacy

        self.tweet_df['tokens'] = self.tweet_df['text'].apply(lambda text: self.partial_preprocess(text))
        # remove both gensim and custom stopwords
        self.tweet_df['tokens'] = self.tweet_df['tokens'].apply(lambda x: self.post_process_stopwords(x))

    def clean_tokenize_text_only_gensim(self, trunc_df: bool = False):
        """
            A function that cleans and tokenizes the text in the column 'text' and saves it in a column called 'gensim_tokens'. Gensim tokens are stems as opposed to the lemmas created by SpaCy
            These are the changes we'll see performed on the original 'text':
            - remove tags
            - strip punctuation
            - remove multiple whitespace
            - remove numeric characters
            - tokenize words
            - return a lower-case stemmed version of the text
            - remove common STOPWORDS (imported from gensim's Stone, Denis, Kwantes (2010) dataset)
            - remove CUSTOM_STOP_WORDS, defined above
        """

        if trunc_df:
            self.tweet_df = self.tweet_df.iloc[:self.trunc_data_length, :].copy()

        self.tweet_df['text'] = self.tweet_df['text'].astype(str)
        # # remove profanity: this slows things considerably and so commenting Out
        # self.tweet_df['text'] = self.tweet_df['text'].apply(lambda text: profanity.censor(text))
        # #Use Gensim's preprocess and create Gensim tokens that can be recognized by its corpora
        self.tweet_df['gensim_tokens'] = self.tweet_df['text'].apply(lambda text: preprocess_string(text))

        # remove both gensim and custom stopwords
        self.tweet_df['gensim_tokens'] = self.tweet_df['gensim_tokens'].apply(lambda x: self.post_process_stopwords(x))

    def append_bigrams(self, use_gensim_tokens: bool = False):
        """
            A function that appends bigrams (sets of two adjacent words) for the column 'tokens' or gensim_tokens based on where we want to use Spacy lemmas orgensim token

            Use gensim's gensim.models.Phrases to detect the frequent bigrams, and then "freeze" the model as a Phraser for better performance.

            Only do this for bigrams that appear together frequently in the corpus (20+ times) so that it makes sense to treat them as a single phrase. (min_count parameter)

            Join the bigrams using an underscore or "_" (delimiter parameter, also the default treatment);
            e.g., the tokens ['machine','learning'] would yield ['machine','learning', 'machine_learning']

        NOTE: Don't remove duplicate strings. It's OK if the same bigram is included more than once.
        """

        if use_gensim_tokens:
            col_name = 'gensim_tokens'
        else:
            col_name = 'tokens'
        self.bigrams = Phrases(self.tweet_df[col_name], min_count=20)
        self.frozen_bigrams_model = self.bigrams.freeze()
        self.tweet_df[col_name] = self.tweet_df[col_name].apply(lambda x: self.frozen_bigrams_model[x])

    def find_lda_topics(self, num_topics, trunc_df: bool = True):
        """

        :param num_topics: Number of topics to create the LDA model with
        :param trunc_df: When running an evaluation for picking models, set trunc_df = True so that we work on a smaller dataset
        :return: top topics found by model
        Use gensim's LDA Model to find num_topics and return the top_topics. These are parameters for the LDA Model:
            - chunksize=2000
            - passes=20
            - iterations=400
            - eval_every=None
            - random_state=42
            - alpha='auto'
            - eta='auto'
        """

        # use gensim's Dictionary to filter words that appear less than ten times in the corpus
        # or represent more than 60% of the corpus
        # use the dictionary to create a bag of word representation of each document
        if trunc_df:
            tokens = self.tweet_df.iloc[:self.trunc_data_length, :]['gensim_tokens'].dropna()
        else:
            tokens = self.tweet_df['gensim_tokens'].dropna()

        corpus = list(tokens.values)
        dictionary = Dictionary(corpus)
        dictionary.filter_extremes(no_below=10, no_above=0.6)  # Change and check output
        common_corpus = [dictionary.doc2bow(text) for text in corpus]
        # print([[(dictionary[id], freq) for id, freq in cp] for cp in common_corpus[:1]])
        lda_model = LdaModel(common_corpus,
                             id2word=dictionary,
                             num_topics=num_topics,
                             chunksize=2000,
                             passes=20,
                             iterations=400,
                             eval_every=None,
                             random_state=42,
                             alpha='auto',
                             eta='auto')
        # Save the model

        lda_model.save(f'{self.lda_model_saved_path}lda_model_topics_{num_topics}.model')
        top_topics = lda_model.top_topics(common_corpus)
        return top_topics

    def calculate_lda_avg_coherence(self, topics):
        """
        This function computes the average coherence score for a list of topics
        topics: a sequence of topics as extraced from an LDA model

        """
        avg_topic_coherence = sum([t[1] for t in topics]) / len(topics)
        return avg_topic_coherence

    def get_lda_topic_coherences_data(self, min_topics: int = 2, max_topics: int = 6, trunc_df: bool = True):
        """
        Creates data for coherence for the topic models created with num_topics varying from 2 to 10
        """
        ## Set up the topics and dictionary
        if trunc_df:
            corpus = list(self.tweet_df.iloc[:self.trunc_data_length, :]['gensim_tokens'].dropna().values)
        else:
            corpus = list(self.tweet_df['gensim_tokens'].dropna().values)

        dictionary = Dictionary(corpus)
        dictionary.filter_extremes(no_below=10, no_above=0.6)
        # range of topics
        topics_range = range(min_topics, max_topics + 1, 1)
        coherence_list = []
        top_topics_list = []
        for num_topics in topics_range:
            top_topics = self.find_lda_topics(num_topics=num_topics)
            coherence_list.append(self.calculate_lda_avg_coherence(top_topics))
            top_topics_list.append(top_topics)

        model_results = {'Num Topics': topics_range, 'Coherence': coherence_list, 'Topics': top_topics_list}
        # plt = pd.DataFrame(model_results).set_index('Topics').plot()
        return pd.DataFrame(model_results).set_index('Topics')

    # define function to get words in topics
    # https://gist.github.com/rrpelgrim/c5e72bd0654d10a875ebeb6715869a95
    def get_topics_lists(self, mgp, top_topics: list = [0, 1, 2, 3], n_words: int = 10):
        '''
        Gets lists of words in topics as a list of lists.

        model: gsdmm instance
        top_clusters:  numpy array containing indices of top_clusters
        n_words: top n number of words to include

        '''
        # create empty list to contain topics
        topics = []
        # iterate over top n clusters
        for topic in top_topics:
            # create sorted dictionary of word distributions
            sorted_dict = sorted(mgp.cluster_word_distribution[topic].items(), key=lambda k: k[1], reverse=True)[
                          :n_words]
            # create empty list to contain words
            topic = []
            # iterate over top n words in topic
            for k, v in sorted_dict:
                # append words to topic list
                topic.append(k)
            # append topics to topics list
            topics.append(topic)
        return topics

    def get_mgp_topic_clusters(self, max_num_topics: int = 4, alpha: float = 0.1, beta: float = 0.1,
                               trunc_df: bool = True):
        """

        As per paper : https://dbgroup.cs.tsinghua.edu.cn/wangjy/papers/KDD14-GSDMM.pdf

        :param max_num_topics:
        :return:
        """

        if trunc_df:
            docs = self.tweet_df.iloc[:self.trunc_data_length, :]['tokens'].dropna().values
        else:
            docs = self.tweet_df['tokens'].dropna().values

        # Using Spacy's lemmatized text does not populate a dictionary and so we do not calculate coherence

        mgp = MovieGroupProcess(K=max_num_topics, alpha=alpha, beta=beta, n_iters=30)
        vocab = set(term for doc in docs for term in doc)
        n_terms = len(vocab)
        _ = mgp.fit(docs, n_terms)

        # save_mgp_model the model
        self.save_mgp_model(mgp, max_num_topics)

        return mgp

    def top_words(self, cluster_word_distribution, top_cluster, values):
        for cluster in top_cluster:
            sort_dicts = sorted(cluster_word_distribution[cluster].items(), key=lambda k: k[1], reverse=True)[:values]
            print(f"\nCluster {cluster} : {sort_dicts}")
            return sort_dicts

    def get_mgp_details(self, mgp, num_topics):
        # get count of documents assigned to each of the latent topics
        doc_count = np.array(mgp.cluster_doc_count)
        print('Count of documents per topic :', doc_count)
        print('--' * 20)
        # Sorted the topics by the number of document they are allocated to
        top_index_list = doc_count.argsort()[-10:][::-1]
        print(f'Most important topics (based on number of docs): {top_index_list}')
        print('--' * 20)
        # Show the top 5 words in term frequency for each topic
        top_words = self.top_words(mgp.cluster_word_distribution, top_index_list, 10)
        return (doc_count, top_index_list, top_words)

    def get_mgp_coherence_data(self, num_clusters, alpha: int, beta: int, trunc_df: bool = False):
        """
        This function determines the calculated coherence value for a range of max_topic values for GSDMM so that we can decide on optimum number of clusters.
        Although GSDMM uses maximum number of clusters as a suggestion and is supposed to return only the number of clusters that provide best clustering, I have only seen it return all the clusters
        :param num_clusters:
        :param alpha: See explanation above. (probability of moving to a table)
        :param beta: See explanation above. (choose a tbale with similar list of movies)
        :return:

        """
        # coherence_mgp_list = []
        topic_details_list = []
        for k in list(range(num_clusters))[2:]:
            topic_details = dict()
            mgp = self.get_mgp_topic_clusters(max_num_topics=k, alpha=alpha, beta=beta, trunc_df=trunc_df)
            # coherence_mgp_list.append(coherence_mgp)
            topic_details['doc_count'], topic_details['top_index_list'], topic_details[
                'top_words'] = self.get_mgp_details(mgp, num_topics=k)
            topic_details_list.append(topic_details)
        return pd.DataFrame({"Number of topics": list(range(num_clusters))[2:], "Topic Details": topic_details_list})

    def save_mgp_model(self, mgp, num_topics: int):
        if self.gdrive_file_path:
            model_file_path = f"/content/drive/MyDrive/Capstone/data/social_media_data/models/gsdmm_models/gsdmm_{num_topics}.pickle"
        else:
            model_file_path = f"../data/social_media_data/models/gsdmm_models/gsdmm_{num_topics}.pickle"

        with open(model_file_path, 'wb') as handle:
            pickle.dump(mgp, handle)
            handle.close()

    def load_lda_model(self, num_topics):
        """
            Load the lda model created  with num_poics
        :param num_topics: Number of topics the model was created with
        :return: returns an lda model previously created
        """
        # later on, load trained model from file
        model = LdaModel.load(f'{self.lda_model_saved_path}lda_model_topics_{num_topics}.model')
        return model

    def load_mgp_model(self, num_topics):
        """
            Load the mgp model created  with num_poics
        :param num_topics: Number of topics the model was created with
        :return: returns an lda model previously created
        """
        # later on, load trained model from file

        if self.gdrive_file_path:
            model_file_path = f"/content/drive/MyDrive/Capstone/data/social_media_data/models/gsdmm_models/gsdmm_{num_topics}.pickle"
        else:
            model_file_path = f"../data/social_media_data/models/gsdmm_models/gsdmm_{num_topics}.pickle"

        with open(model_file_path, 'rb') as handle:
            model = pickle.load(handle)
        return model

    def create_topics_dataframe(self, mgp, threshold: int = 0.3):
        """
        :param mgp: Model chosen to apply on the dataframe for labeling
        :param threshold: a minimum probability returned by choose_best_label above which the returned cluster number is accepted as the label
        :return: None
        """

        def apply_best_label(token):
            # print(token)
            prob = mgp.choose_best_label(token)

            # prob[1] contains the probability of a document being in prob[0] (which is the cluster or topic_num index)
            if prob[1] >= threshold:
                # Prob[0] contains the cluster number
                return f"Topic {prob[0]}"
            else:
                return "Other"

        self.tweet_df['Unsupervised Learning Label'] = self.tweet_df['tokens'].apply(
            lambda token: apply_best_label(token))

        # In addition to the unsupervised learning, we will assign those tweets that have Disney hashtags to the entertainment section
        self.tweet_df['Entertainment'] = self.tweet_df['hashtags'].fillna("").str.replace(
            "[", "",
            regex=False).str.replace("]",
                                     "",
                                     regex=False).str.lower().str.contains(
            'wdw|disney|walt|animalkigdom|themepark|tv|movie')
        self.tweet_df['Final Label'] = np.where(self.tweet_df['Entertainment'],
                                                'Off_topic',
                                                np.where((self.tweet_df['Unsupervised Learning Label'] == 'Topic 0') |
                                                         (self.tweet_df['Unsupervised Learning Label'] == 'Topic 1') |
                                                         (self.tweet_df['Unsupervised Learning Label'] == 'Topic 3'),
                                                         "Everest_topic", 'Off_topic'))

    def create_scatter_text_html(self, read_from_disk:bool=True, html_file_path:str= "../visualization_data/Everest_Visualization_Two_topics.html"):
        """
        :param read_from_disk: If set, this function returns an html read from a file on the disk
        :param read_from_disk:File path of html

        This function takes a unsupervised labeled dataset with two categories (since scatter text works with two categories) then it parses the lemmatized tokens and performs clustering.
        Based on a score scatter text places the words representative of
        :return: The generated html
        """
        if read_from_disk:
            html = pd.read_html(html_file_path)
            return html

        else:
            # To balance the data in visualization, we pick as many of the Everest topic tweets as limited by the number of Off-topic tweets
            value_list = []
            value_list.append(self.tweet_df[self.tweet_df['Final Label'] == 'Off_topic'].shape[0] / 1000)
            max_size = int((np.floor(value_list) * 1000)[0])
            visual_df = pd.concat([self.tweet_df[self.tweet_df['Final Label'] == 'Everest_topic'].sample(max_size),
                                   self.tweet_df[self.tweet_df['Final Label'] == 'Off_topic'].sample(
                                       max_size)], axis='rows')[['Final Label', 'tokens']].copy()
            # Join all the tokens so that scattertext can parse it and create the same tokens again!
            visual_df['token_text'] = visual_df['tokens'].apply(lambda token_list: " ".join(token_list))

            print(visual_df[visual_df['Final Label'] == 'Everest_topic'].sample(1))

            print(visual_df[visual_df['Final Label'] == 'Off_topic'].sample(1))

            visual_df = visual_df.assign(
                parse=lambda df: visual_df['token_text'].apply(st.whitespace_nlp_with_sentences)
            )

            # Parse the tokens and assign the labels to a column called label. Shorten the labels themselves Since we are applying nlp this can take a long time to run ~about 15 mins on a CPU
            visual_df = visual_df.assign(
                parse=lambda visual_df: visual_df['token_text'].apply(nlp),
                label=lambda visual_df: visual_df['Final Label'].apply(
                    {'Everest_topic': 'Everest', 'Off_topic': 'Entertainment'}.get)
            )

            print(visual_df.sample())
            #
            corpus = st.CorpusFromParsedDocuments(
                visual_df,
                category_col='label',
                parsed_col='parse'
                # feats_from_spacy_doc=st.PyTextRankPhrases()
            ).build(
            ).get_unigram_corpus(
            ).compact(
                st.AssociationCompactor(2000)
            )

            html = st.produce_scattertext_explorer(corpus,
                                                   category='Everest',  # the "base" category
                                                   category_name='Everest',
                                                   # the label for the category (same in this case,
                                                   not_category_name='Entertainment',
                                                   width_in_pixels=1000
                                                   )

            #Save the corpus and generated html
            with open(os.path.join("..", "data", "social_media_data", "visual_creation_data", "st_corpus_two_topics.pickle"), "wb") as handle:
                pickle.dump(corpus, handle)
            # Open a file for writing using the `with` statement
            with open(html_file_path, 'wb') as handle:
                # Write the HTML string to the file
                handle.write(html.encode('utf-8'))
            handle.close()
            return html
