import os
import pickle

import pandas as pd
import regex as re
import tweepy
from datetime import date
import snscrape.modules.twitter as sns


class SocialMediaDataCollection():
    """
        This class sets credentials and retrieves Twitter user and tweet data
    """

    def __init__(self, cred_file_path: str = '../passwords/twitter_auth_academic.pickle'):
        """

        :param cred_file_path: pathfile to the pickle file containing the credentialing values
        """
        with open(cred_file_path, 'rb') as handle:
            twitter_auth = pickle.load(handle)

        # https://docs.tweepy.org/en/stable/client.html
        client = tweepy.Client(bearer_token=twitter_auth['bearer_token'],
                               consumer_key=twitter_auth['API_Key'],
                               consumer_secret=twitter_auth['API_Key_secret'],
                               access_token=twitter_auth['Access_token'],
                               access_token_secret=twitter_auth['Access_token_secret'],
                               wait_on_rate_limit=True)

        auth = tweepy.OAuth1UserHandler(
            twitter_auth['API_Key'],
            twitter_auth['API_Key_secret'],
            twitter_auth['Access_token'],
            twitter_auth['Access_token_secret'],

        )

        api = tweepy.API(auth, wait_on_rate_limit=True)
        print("")
        self.client = client
        self.api = api
        my_creds = api.verify_credentials()
        print(f"Credentials Name:{my_creds.name} and screen_name:{my_creds.screen_name}")

    def get_influencer_seeds(self, influencers_list):
        """
        This function creates a dict and saves a dataframe of seeed influencers in twitter

        :param influencers_list: The list of usernames of influencers
        :return: A dict of user and characteristics. It also saves the user info into a csv
        """
        client = self.client
        seed_influencers_data = []

        for seed in influencers_list:
            influencer_dict = {}
            user = client.get_user(username=seed)
        # acess public_metrics which provides counts of followers, following ...
            user = client.get_user(username=seed,
                                   user_fields=['url', 'public_metrics'],
                                   expansions=['pinned_tweet_id'])

            if not user is None:
                influencer_dict['id'] = user.data.id
                influencer_dict['user_name'] = user.data.name
                influencer_dict['screenname'] = user.data.username

                influencer_dict['followers_count'] = user.data.public_metrics['followers_count']
                influencer_dict['following_count'] = user.data.public_metrics['following_count']
                influencer_dict['tweet_count'] = user.data.public_metrics['tweet_count']
                influencer_dict['listed_count'] = user.data.public_metrics['listed_count']

                influencer_dict['pinned_tweet_id'] = user.data.pinned_tweet_id
                seed_influencers_data.append(influencer_dict)


        pd.DataFrame(seed_influencers_data).to_csv("../data/social_media_data/seed_influencers_df.csv",
                                                   index=False)
        return seed_influencers_data


    def get_user_statistics(self, user_list):
        """
              This function creates a dataframe of twitter users provided in the user list but it also saves information into a CSV file every
              200 users

              :param influencers_list: The list of twitter usernames
              :return: A dict of user and characteristics. It also saves the user info into a csv for every 200 user
        """
        client = self.client
        user_data_list = []
        for user_num, one_user in enumerate(user_list):
            user_dict = {}

            # get user data
            user = client.get_user(username=one_user,
                                   user_fields=['url', 'public_metrics'],
                                   expansions=['pinned_tweet_id'])

            if not user is None:
                user_dict['id'] = user.data.id
                user_dict['user_name'] = user.data.name
                user_dict['screenname'] = user.data.username

                user_dict['followers_count'] = user.data.public_metrics[
                    'followers_count']
                user_dict['following_count'] = user.data.public_metrics[
                    'following_count']
                user_dict['tweet_count'] = user.data.public_metrics['tweet_count']
                user_dict['listed_count'] = user.data.public_metrics['listed_count']

                user_dict['pinned_tweet_id'] = user.data.pinned_tweet_id
                user_data_list.append(user_dict)
                # save periodically (every 200th user)
                if user_num != 0 and user_num % 200 == 0:
                    pd.DataFrame(user_data_list).to_csv(f"../data/social_media_data/user_attributes_df_{user_num}.csv",
                                                        index=False)
        # Save the last non-divisible by 200 chunk
        pd.DataFrame(user_data_list).to_csv(f"../data/social_media_data/user_attributes_df_{len(user_list)}.csv",
                                            index=False)
        return user_data_list


    def get_user_following_df(self, user_id, username):
        """
        This function calls Twitter get_users_following to get the list of users ta certain influencer is following

        :param user_id: The twitter user id for whom we need to the get the users ids they are following
        :param username: he twitter user id for whom we need to the get the users ids they are following
        :return: It save the data in a csv
        """
        client = self.client
        paginator = tweepy.Paginator(
            client.get_users_following,  # get users following
            user_id,  # this user id
            max_results=200,  # limit results
            # typically you can place your limit here but if you do not ,make sure you indicate
            # rate limit
            limit=10)

        following_user_id_list = []
        following_username_list = []

        try:
            for responses in paginator:
                for response in responses.data:
                    following_user_id_list.append(response.data["id"])
                    following_username_list.append(response.data["username"])
        except tweepy.TooManyRequests as exc:
            print('Rate limit!')
            # time.sleep(60 * 15)

        # Save each user following list
        pd.DataFrame({
            "id": following_user_id_list,
            "screen_name": following_username_list
        }).to_csv(f"../data/social_media_data/influencer_{username}_follows_df.csv", index=False)
        return


    def get_followers_of_influencer_seed(self,  user_id, username):
        """
        This function calls Twitter get_users_following to get the list of users ta certain influencer is following

        :param user_id: The twitter user id for whom we need to the get the users ids they are following
        :param username: The twitter user id for whom we need to the get the users ids they are following
        :return: It saves the data in a csv
        """
        client = self.client
        paginator = tweepy.Paginator(
            client.get_users_followers,  # get users following
            user_id,  # this user id
            max_results=200,  # limit results
            # typically you can place your limit here but if you do not ,make sure you indicate
            # rate limit
            limit=10)

        following_user_id_list = []
        following_username_list = []

        try:
            for responses in paginator:
                for response in responses.data:
                    following_user_id_list.append(response.data["id"])
                    following_username_list.append(response.data["username"])
        except tweepy.TooManyRequests as exc:
            print('Rate limit!')
            # time.sleep(60 * 15)

        # Save each user following list
        pd.DataFrame({
            "id": following_user_id_list,
            "screen_name": following_username_list
        }).to_csv(f"../data/social_media_data/influencer_{username}_followedby_df.csv", index=False)
        return

    def create_influence_network(self) -> pd.DataFrame:
        user_following_files = [
            file for file in os.listdir()
            if "influencer" in file and 'follows' in file
        ]
        influencers_df = pd.read_csv("influencers_df.csv")
        full_df = pd.DataFrame()
        for filename in user_following_files:
            m = re.search('influencer_(.+?)_follows_df.csv', filename)
            if m:
                screenname = m.group(1)
                # print(screenname)
                indv_df = pd.read_csv(filename)
                indv_df['influencer_screenname'] = screenname
                indv_df['influencer_id'] = influencers_df[
                    influencers_df['screenname'] == screenname]['id'].values[0]

                full_df = pd.concat([full_df, indv_df])
        full_df.to_csv("influencers_network.csv", index=False)
        return full_df


    def save_nodes_and_network(self, influencer_network_df: pd.DataFrame):
        node_list = pd.concat([
            influencer_network_df[['id',
                                   'screenname']].rename(columns={
                'id': 'Id',
                'screenname': 'Label'
            }),
            influencer_network_df[['influencer_id', 'influencer_screenname'
                                   ]].rename(columns={
                'influencer_id': 'Id',
                'influencer_screenname': 'Label'
            })
        ])
        node_list.drop_duplicates(inplace=True)
        node_list.to_csv('Node_Attributes.csv', index=False)
        influencer_network_df = influencer_network_df[[
            'influencer_id', 'id'
        ]].rename(columns={
            'influencer_id': 'source',
            'id': 'target'
        })
        influencer_network_df.to_csv('Influencer_Network.csv', index=False)
        return


    def get_labeled_influencer_network(self):
        influencer_network_df = pd.read_csv('Influencer_Network.csv')
        node_attribute_df = pd.read_csv('Node_Attributes.csv')

        influencer_network_df = pd.merge(influencer_network_df,
                                         node_attribute_df,
                                         left_on='source',
                                         right_on='Id',
                                         how='inner'
                                         ).drop(
            columns=['Id']
        ).rename(columns={'Label': 'Source Label'}
                 )
        influencer_network_df = pd.merge(
            influencer_network_df,
            node_attribute_df,
            left_on='target',
            right_on='Id',
            how='inner'
        ).drop(
            columns=['Id']
        ).rename(
            columns={'Label': 'Target Label'}
        )

        return influencer_network_df


    def user_limited_nodes(self, num_common_influencers_following: int, min_followers_count: int,
                           min_tweet_count: int) -> pd.DataFrame:
        influencer_network_df = self.get_labeled_influencer_network()
        user_attributes_dict = pd.read_csv('user_attributes_df_6504.csv')

        influencer_list = influencer_network_df.groupby(['Source Label']).count().sort_values(by=['source'],
                                                                                              ascending=False).index.values
        infleuncer_node_df = user_attributes_dict[user_attributes_dict['screenname'].isin(influencer_list)]

        # Can you add to the dataframe how many of the influencers follow these users
        targets_followed = influencer_network_df[['Source Label', 'Target Label']].groupby('Target Label').count()
        targets_followed = targets_followed.reset_index().rename(
            columns={'Source Label': 'common_influencers_following'})

        # concat the users most followed by the influencers with the influencers themselves
        # This will eliminate individual influencer preferences
        most_followed_df = pd.merge(targets_followed, user_attributes_dict, left_on='Target Label',
                                    right_on='screenname',
                                    how='inner').drop(columns='Target Label')
        influencers_df = user_attributes_dict[user_attributes_dict['screenname'].isin(influencer_list)]
        user_limited_df = pd.concat([most_followed_df, influencers_df])
        # Set the common_influencers_follwoing to a very high number for the infleuncers themselves
        # Limit the targets or the users that the influencers are following to those that are being followed by more than two influencers
        user_limited_df = user_limited_df[(user_limited_df['common_influencers_following'].isna()) | (
                user_limited_df['common_influencers_following'] >= num_common_influencers_following)].copy()
        user_limited_df = user_limited_df[(user_limited_df['tweet_count'] >= min_tweet_count) & (
                user_limited_df['followers_count'] >= min_followers_count)].copy()

        return user_limited_df


    def save_nodes_edges(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame):
        nodes_df.to_csv('user_limited_nodes_df.csv', index=False)
        edges_df.to_csv('user_limited_network_df.csv', index=False)


class TweetScraper():
    def __init__(self, start_date: date, end_date: date, keyword_str: str, max_tweets: int = 1000,
                 lang_str: str = " lang:en"):

        """ This function sets up the basic parameters for the SNSCRAPE module"""
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.end_date = end_date.strftime('%Y-%m-%d')
        self.max_tweets = max_tweets
        self.colnames = ['date', 'text', 'userid', 'likeCount', 'replyCount', 'retweetCount', 'coordinates', 'hashtags']

        # How to collect tweets with quality filters: https://developer.twitter.com/en/docs/tutorials/building-high-quality-filters
        # keyword = '(everest himalayas) OR (himalayas expedition) OR (climb everest) OR (everest expedition) lang:en -is:retweet'
        self.keyword_str = keyword_str
        self.lang_str = lang_str
        time_range = ' since:' + self.start_date + ' until:' + self.end_date + ' '
        filters = ' -filter:links -filter:replies '
        self.query = self.keyword_str + time_range + filters + lang_str
        print(self.query)

    def get_scraped_tweets(self):
        """
            This function uses snscrape to retrieve tweets in a given time range limited to max_tweets
        :return:
        """
        curr_df = pd.DataFrame()
        tweet_data_list = []
        for tweet_num, catch_tweet in enumerate(sns.TwitterSearchScraper(self.query).get_items()):
            this_tweet_data_list = [catch_tweet.date, catch_tweet.content, catch_tweet.user.id, catch_tweet.likeCount,
                                    catch_tweet.replyCount, catch_tweet.retweetCount, catch_tweet.coordinates,
                                    catch_tweet.hashtags]
            tweet_data_list.append(this_tweet_data_list)
            if tweet_num > self.max_tweets:
                break
        self.tweet_df = pd.DataFrame(tweet_data_list, columns=self.colnames)
        return

    def save_tweets_for_period(self):
        period = self.start_date + "-to-" + self.end_date
        self.tweet_df.to_csv(f"../data/social_media_data/tweet_search_data/tweets-{period}.csv", index=False)

    def save_tweets_from_account(self, account_name):
        self.tweet_df.to_csv(f"../data/social_media_data/tweet_search_data/tweets-from-{account_name}.csv", index=False)