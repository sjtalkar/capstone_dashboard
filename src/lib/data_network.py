import os
import pandas as pd
import pickle
import tweepy
import regex as re

def create_influence_network() -> pd.DataFrame:
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


def save_nodes_and_network(influencer_network_df: pd.DataFrame):
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


def get_labeled_influencer_network():
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


def user_limited_nodes(num_common_influencers_following: int, min_followers_count: int,
                       min_tweet_count: int) -> pd.DataFrame:
    influencer_network_df = get_labeled_influencer_network()
    user_attributes_dict = pd.read_csv('user_attributes_df_6504.csv')

    influencer_list = influencer_network_df.groupby(['Source Label']).count().sort_values(by=['source'],
                                                                                          ascending=False).index.values
    infleuncer_node_df = user_attributes_dict[user_attributes_dict['screenname'].isin(influencer_list)]

    # Can you add to the dataframe how many of the influencers follow these users
    targets_followed = influencer_network_df[['Source Label', 'Target Label']].groupby('Target Label').count()
    targets_followed = targets_followed.reset_index().rename(columns={'Source Label': 'common_influencers_following'})

    # concat the users most followed by the influencers with the influencers themselves
    # This will eliminate individual influencer preferences
    most_followed_df = pd.merge(targets_followed, user_attributes_dict, left_on='Target Label', right_on='screenname',
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


def save_nodes_edges(nodes_df: pd.DataFrame, edges_df: pd.DataFrame):
    nodes_df.to_csv('user_limited_nodes_df.csv', index=False)
    edges_df.to_csv('user_limited_network_df.csv', index=False)
