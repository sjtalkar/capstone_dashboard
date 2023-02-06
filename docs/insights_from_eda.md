**Insights from Himalayan dataset through**

**Exploratory Data Analysis**

The Himalayan dataset consists of three primary information structured
data: the peaks, expeditions and members datasets. The exploratory
analysis attempts to provide a convenient form of analysis of the data
as it was available in Spring of 2022.Questions that can be answered
through the visualizations in the exploratory analysis revolve around
peak popularity, member profiles and expedition characteristics.

**Member data analysis**

People with diverse backgrounds undertake expeditions on the Himalayan
ranges. The dataset reveals interesting aspects of membership such as
age of the members as recorded for analysis on a significant date of the
expedition undertaken by the member. The date at which the age is
recorded can be date of summitting, date of death, date of arrival at
base camp or date of the start of the season. Members arrive from all
over the world, and we can segment them by nationality (category data),
in addition to age and gender. In the parallel co-ordinates plot, a
range of feature values for members segmented by nationality is
presented for analysis and insights. In order to facilitate ease in
choice of nationality from over 100 countries, groups of countries are
created based on number of unique members from the country. In addition
to viewing from a range choice of top 10 countries to top 40 countries
with most members, the user can choose to any one or more of other
countries, in addition to the groups, for comparison with the selected
group.

Parallel axes with continuous values that the user can choose from range
from number of members, hired, leaders, injured, deaths, deaths due to
weather, oxygen usage, solo attempts, high camp reached, women, base
camp only expeditions (as opposed to summitting), and high point
reached.

Age (Lowest, Median, Highest) : This reveals expeditioners as young as 7
years of age (from Italy) and as old as 85 years of age from Nepal have
climbed the range in expeditions. While for most countries the lowest
range is in late teens or early twenties, expeditioners from Nepal can
be as young as 12. These young expeditioners might trek up to the Base
Camp but not beyond. But there are expeditioners as young as 13 who have
reached the high point such as Malavath, Poorna from India. The median
age across the countries is from 30 to early 40s. While Nepal can boast
of climbers in their 80s, for many other countries early 70s is the
highest age of attempt.

Registered members are the highest for USA which can claim over 3700
expeditioners followed by Japan and UK. But it also shows that many
expeditioners may have travelled only to the base camp and not trekked
all the way to the summit. Most women expeditioners are also from the
US. France has the most expeditioners who prefer to go it alone. And
while unsurprisingly many of the hired expeditioners are from Nepal,
Spain has the largest fraction of members who are leaders as per the
normalized chart that shows numbers normalized by the number of member
expeditioners from a country.

Oxygen usage percentage is highest for expeditioners from Nepal and US
and Japanese expeditioners have suffered the most deaths due to weather.

Besides raw counts, this page allows one to look into the percentage
value in each of the feature parallel axes where the data is normalized
by the number of unique member expeditioners from each country.

<img src=".\/media/image1.png" style="width:6.5in;height:3.15833in" />

**Commercial and Non-Commercial expeditions**

In the Himalayan dataset of Spring 2022, we have information about
whether the expedition is commercial or non-commercial in 78% of the
expedition records. The popularity of mountaineering and expeditions in
the Himalayan mountain ranges have skyrocketed in the past few decades (
the spatial analysis graph is a strong indicator of this). There are
several guided expedition organizers that support people interested in
scaling these peaks. This page supports the analysis in distribution of
features by year for commercial versus non-commercial expeditions.

As per the dataset, we have information for five peaks with commercial
expeditions: Ama Dablam, Cho You, Everest, Lhotse and Manaslu. On this
page we can isolate the averages and counts for successful expeditions
versus others. When applying average over all expeditions, average of
number of days to summit and total days are averaged over expeditions
that might have terminated prior to reaching a high point or even a base
camp.

For Everest, we see that for non-commercial routes there was a peak in
oxygen usage in the 90’s followed by a dip until 2022. Member deaths
interestingly fell during these years as well and drastically reduced in
the 2020s. Similarly for commercial routes, the oxygen usage steadily
rose while member deaths crept lower.

<img src=".\/media/image2.png" style="width:6.5in;height:1.85972in" />

But it is also interesting to note that the number of expeditions that
are non-commercial dwindle to nearly zero in the past few years. We also
see the pandemic having a effect on expeditions since borders were
closed.

<img src=".\/media/image3.png"
style="width:3.67974in;height:2.16499in" />

For both a 8000er like Everest and a 6000er like Ama Dablam, we see the
average number of days to summit from base for successful expeditions
decline since 2000 for commercial expeditions.

Everest:

<img src=".\/media/image4.png" style="width:2.76054in;height:1.52419in"
alt="Chart Description automatically generated" />

Ama Dablam:

<img src=".\/media/image5.png" style="width:2.73375in;height:1.5649in"
alt="Graphical user interface, chart Description automatically generated" />

Lhotse stands out as a peak with very few commercial expeditions through
the decades..

<img src=".\/media/image6.png" style="width:6.5in;height:2.57431in" />

**Commercial Peaks Analysis**

As mentioned above, as per the dataset, we have information for five
peaks with commercial expeditions: Ama Dablam, Cho You, Everest, Lhotse
and Manaslu. In this page we take a deeper dive into data to compare the
commercial expeditions in these five peaks.

At the bottom of the page we see the comparison between commercial or
non-commercial expeditions in terms of reasons of termination for these
peaks. While most expeditions are successful, bad weather followed by
illness, including Acute mountain sickness(AMS) and frost bite often
result in early termination of expeditions.

<img src=".\/media/image7.png" style="width:6.5in;height:2.86111in" />

Selecting range of years from 1990 to present, clearly shows a dip in
expeditions, number of base camps set up and total days of expeditions
to the summit in the year 2015. A web search indicates that this was the
year of the Nepal earthquake. \[Wikipedia: “According to the USGS, the
earthquake was caused by a sudden thrust, or release of built-up stress,
along the major fault line where the Indian Plate, carrying India, is
slowly diving underneath the Eurasian Plate, carrying much of Europe and
Asia.”\]. The pandemic (coronavirus. COVID-19) year also shows a
plummeting of number of expeditions.

<img src=".\/media/image8.png" style="width:6.5in;height:2.17708in" />

The trend shows that the average days to summit for all peaks is
decreasing. For Everest, for instance it went down from an average of 33
days to 21 days. The number of commercial expeditions has been steadily
increasing on the other hand, especially in the 21<sup>st</sup> century.
For Everest about 54% of the expeditions in 1990 were commercial while
in the year 2000, 95% of the expeditions were commercial. The peaks
Lhotse bucks this trend though with very few commercial expeditions as
per the Himalayan dataset.

<img src=".\/media/image9.png" style="width:3.19697in;height:3.09643in" />  
<img src=".\/media/image10.png" style="width:3.16506in;height:3.10944in" />  

Oxygen usage in commercial expeditions has also been rising. Again for
Everest while in the recent years (2018 and onwards) oxygen usage is
between 95% to a 100%, as it has been rising from 68% in 1990. This
trend is also witnessed by other peaks.

In 2014, both Everest and Lhotse saw a spike in percentage of hired
expeditioner deaths. As per
[Wikipedia,](https://en.wikipedia.org/wiki/2014_Mount_Everest_ice_avalanche#:~:text=Sixteen%20people%20died%20in%20the%20disaster.)
an ice avalance caused immense loss in Sherpa (Hired expeditioners)
lives.

<img src=".\/media/image11.png" style="width:3.36749in;height:3.24857in" />

**Peak Popularity Analysis**

The visualizations on this page were created to answer questions such as
:

1.  What is the trend in oxygen usage?

2.  What is the trend in members and number of expeditions in each
    season of years since expeditions became popular in the Himalayas?

3.  Does number of hired personnel follow the same trend as members?

4.  What is the percentage of members and hired personnel that have died
    over the years?

5.  Is there a trend that can be detected in oxygen usage on various
    peaks?

To facilitate analysis and comparison among peaks, the user can select
to group peaks with the most expeditions and then in addition, highlight
and compare other peaks to this group. Peaks with number of expeditions
ranging from 1 to 100 in increments of 10 can be compared with
individual peaks not in the group selected. Individual peaks within the
group can also be highlighted against others in the group.

In the case of oxygen usage, perhaps due to a combination of its height
(8849) and because it attracts so many commercial expeditions,
successful Everest expeditions carry oxygen with a rate of 100%. On Ama
Dablam (6814m) on the other hand, it can be seen, oxygen usage is in
about 5-7% of the expeditions in the past few years. Other peaks
(7000ers) also show less oxygen usage, such as Himlung Himal and
Baruntse with no oxygen usage to a maximum of 25% of expeditions using
oxygen in the past five years. In general in 8000ers such as
Kanchenjunga and Lhotse, there is 100% chance of an expedition using
oxygen.

<img src=".\/media/image12.png" style="width:6.5in;height:1.21181in" />

There is little uncertainty in the most popular peaks in terms of number
of expeditions and number of people interested in climbing them. Everest
is by far the most sought after peak in spring. In the past couple of
decades, Ama Dablam, Manslu and Cho Oyu are popular climbs in fall.

The number of hired personnel peaked right before the pandemic in
Everest at 644 in 2018 and 634 in 2019. The percentage number of deaths
in the past couple of decades in expeditions that continued on to be
successful has been quite low. It has to be recognized that member
deaths might terminate many to most expeditions.

**Peak Route Analysis**

This page provides a look into various routes on each peak and their
popularity as in number of times the routes was taken. The count is
independent of whether the expedition was successful or not. This page
is also useful for lesser popular peaks in investigating into the routes
taken on them. For instance for Dhualagiri I, all the routes are unknown
category or non-commercial:

<img src=".\/media/image13.png" style="width:6.5in;height:3.20139in">

Whereas for a popular peak like Everest, we can clearly pick out the
fully commercial routes in ochre, such as S Col, SE Col-SE Ridge. N
Col-N Ridge-N Face.

<img src=".\/media/image14.png" style="width:6.5in;height:0.96667in">

For the peak Ama Dablam, the route along SW Ridge is favored, though
looking into log counts we see other routes are also pursued
occasionally.

<img src=".\/media/image15.png" style="width:6.5in;height:2.84722in"
alt="Chart Description automatically generated with low confidence" />

<img src=".\/media/image16.png" style="width:6.5in;height:2.89583in">

**Spatial Analysis**

This page is especially useful to track the history of exploration of
Himalayan peaks through the decades. In the visualization columns bars
that are deeper in color indicate taller peaks. The height of the column
indicates the number of expeditions on the peak. The earliest
expeditions (1920-1940) were to peaks that were 6000ers and 7000ers such
as Jongsang, Nepal Peak and Ramtang.

<img src=".\/media/image17.png" style="width:6.5in;height:2.72639in" />

1.  By the 1950s, 8000ers such as Everest, Cho Oyu and Makalu (all in
    the Khumbu-Makalu-Rolwaling region) started to see more expeditions
    but there were a number of other peaks being climbed in the region
    as well.

<img src=".\/media/image18.png" style="width:6.5in;height:3.4in" />

The peak popularity can easily be distinguished in the years past 1950
with Cho Oyu leading the pack, followed by Everest and the shorter Ama
Dablam which is also in the close vicinity. In the first decade of the
21<sup>st</sup> century, Lhotse at 8516 started to also attract more
expeditioners more so than Kanchenjunga (8586 m, Kanchenjunga Janak
region), perhaps because it is closer to Everest.

<img src=".\/media/image19.png" style="width:6.5in;height:3.37917in">

For other 8000ers, climbers chose Dhaulagiri and Manaslu in the
Dahulagiti Mukut region and Manaslu-Ganesh region respectively.

<img src=".\/media/image20.png" style="width:6.5in;height:3.44792in">

**Topic Visualization**

Mountaineers across the world have been tweeting in Twitter about their
upcoming expeditions and challenges they face as well as why they embark
on one from the time Twitter was available as a social platform. Tweets
express sentiments ranging from pride in a country person who has
reached a pinnacle to sharing charities they are climbing for to
expressing admiration for those who overcome personal challenges when
setting off on an expedition. Here are some examples:

- (index 27908) : Anshu Jamsenpa is a mountaineer from Bomdila,
  Arunachal Pradesh. She became the first woman to scale Mount
  Everest twice within five days. \#Knowyourpeople \#AchapterforNE
  \#NortheastMatters

- (index 28954) : A friend of my dad is climbing Mount Everest but is
  also a sufferer of CF, he will be the first person with CF to ever
  take on this task

We are looking for motivating factors that drive people to climb the
Everest and perceptions people have of the trek up the Himalayan
mountains. For instance after exploratory analysis was performed on the
Twitter dataset and we identified those who had scaled not just the
Himalayan mountains but Everest multiple times, the curiosity to
understand why they do it arose. These expeditioners also provide
coaching for others who want to take the journey themselves. Take
accounts of Alan Arnett (@alan_arnette): Summit Coach, Speaker,
Mountaineer, Alzheimer’s Advocate. Oldest American to summit K2 in 2014;
Everest in 2011; and Kenton Cool (@KentonCool) : Climber & lover of good
fish & chips 16 Everest summits & first person to climb Nuptse, Everest
and Lhotse in a season. Speaker, Global Ambassador to @LandRover, for
instance. A summary look into their Twitter posts carry the love they
have for this ‘sport’ and their dedication to this passion which they
share in their talks and through their coaching.

\[Note: Alan Arnette has also been mentioned in the Himalayan Dataset
documents\]

To this end, we approach the social media harvesting of data so that we
can perform Natural Language Processing (unsupervised learning) on the
Twitter posts that mention the ultimate adventure in the Himalayas -
Mount Everest and words related to it.

**Keywords used**

Setting up the right filters involves understanding the results returned
by trying out various filters and using the logical operations of OR,
AND (the default with a space between words) and enclosing multiple word
terms in quotations and using negation operations. For instance, there
is a ride in Disneyland called Mount Everest that showed up in tweets
and so these are removed from the query with a NOT (-). Including
certain words such as base camp ensures we are talking about the climbs
and expeditions and limits the tweets relating to the expeditions.

Keywords included that are unmistakably linked to Everest expeditions:
(Bachendri Pal) OR (Edmund Hillary) OR (Himalayan mountains) OR (everest
expedition) OR (everest base camp) OR (everest trekking) OR (himalaya
base camp) OR \#climbeverest OR “Mount Everest” OR \#EverestBaseCamp  
\[Note: Bachendri Pal is the first Indian woman to climb the summit of
world’s highest mountain, Mount Everest, what she did in 1984.  
Edmund Hillary: On 29 May 1953, Hillary and Sherpa mountaineer Tenzing
Norgay became the first climbers confirmed to have reached the summit of
Mount Everest. \]

Keywords we try to filter out: -Disney -Disneyland -Disneyworld -WDW  
\[Note: Disney has a ride called Expedition Everest that elicits several
tweets from social media users

For example: All the Lightning Lane passes for Expedition Everest -
Legend of the Forbidden Mountain have been given away. \#AnimalKingdom
\#WDW \#WaltDisneyWorld \#DisneyWorld

The distribution of (new) Lightning Lane passes for Expedition Everest -
Legend of the Forbidden Mountain has started. \#AnimalKingdom \#WDW
\#WaltDisneyWorld \#DisneyWorld

\]

Despite this, there were other elements found in the tweets by looking
into the data that suggested we remove text such as WDW which stands for
Walt Disney World and ‘ride’ since Expedition Everest has been a popular
ride at Disney. It is better to retrieve all the data initially and then
filter out the ones relating to entertainment and to the Disney rides.

Timeline : We also harvested tweets for the entire history of Twitter
from some key players such that are focused on expeditions in the
Himalayas.

Despite limiting the tweets, we continued to see topics beyond the
expeditions in the Himalayas. Everest is commonly used as a **metaphor**
for something big and impressive.

- God I can’t go out with Mount Everest on my cheek

- Being sick is when crawling out of bed to walk 12 feet to the bathroom
  feels like climbing Mount Everest. Bed: warm. Everywhere else: cold.

**Unsupervised topic modeling** through the usage of the Gibbs Sampling
Dirichlet Multinomial Mixture method reveals motivations and areas of
interests among the Twitter users who tweet about Mount Everest and
expedition related topics. We seek to identify three clusters of tweets
as mentioned above:

1.  Disney Expedition Everest Ride

2.  Analogy for unsurmountable task or a very large thing

3.  The trekking tweets related to Himalayan expedition. (our topic of
    interest)

**Preparation of tweets for topic modeling**

The tweets are cleaned by using Gensim’s partial preprocess because
although we want to do the below as a part of the preprocessing, we do
not want to stem the words, but instead lemmatixe them using SpaCy.

\- remove tags  
- strip punctuation  
- remove multiple whitespace  
- remove numeric characters  
- tokenize words  
- return a lower-case stemmed version of the text  
- remove common STOPWORDS (imported from gensim's Stone, Denis, Kwantes
(2010) dataset)  
- remove CUSTOM_STOP_WORDS, defined above

**GSDMM**

The Gibbs Sampling Dirichlet Mixture Model (GSDMM) is an “altered” LDA
algorithm, showing great results on Short Text Topic Modeling tasks,
that makes the initial assumption: 1 topic ↔️1 document. The words
within a document are generated using the same unique topic, and not
from a mixture of topics as it was in the original LDA.

“Imagine a bunch of students in a restaurant, seating randomly at K
tables. They are all asked to write their favorite movies on a paper
(but it must remain a short list). The objective is to cluster them in
such a way that so students within the same group share the same movie
interest. To do so, one after another, students must make a new table
choice regarding the two following rules:

Rule 1: Choose a table with more students. This rule improves
completeness, all students sharing the same movie’s interest are
assigned to the same table.

Rule 2: Choose a table where students share similar movie’s interest.
This rule aims to increase homogeneity, we want only members sharing the
same movie’s interest at a table.

Hyperparameters to tune  
K= Maximum Number of clusters or topics  
Alpha = relates to the prior probability of a student (document)
choosing a table (cluster). If we set α = 0, a table will never be
chosen by the students once it gets empty. When α gets larger, the
probability  
of a student choosing an empty table will also get larger.  
Beta : (Choose a table whose students share similar interests with
him/her). If we set β = 0, a student will never choose a table when its
movie lists do not contain a movie of the student. We can see this is
not reasonable,  
because other movies of the student may appear many times in that table
and he/she may share many similar interests with the students of that
table.

Always choose K bigger than the expected number of clusters but
generally with the same order of magnitude as the expected number. If
the number of clusters remains constant across all iterations, you may
not have chosen a large enough value of K. Note, however, that large K
significantly increases the computation time.  
Alpha and beta need to be tuned for each data set and use case. Alpha
and beta tend to work in opposite directions, and they significantly
impact the convergence behavior. It’s usually sufficient to start with a
subsample of documents to get ballpark estimates for these parameters.  
Monitor the number of clusters and the number of docs transferred at
each iteration. Both should die off quickly and then stabilize.
Generally, neither number should increase significantly in subsequent
iterations.

\[Note: There is no pypi install. Install command : pip install
git+https://github.com/rwalk/gsdmm.git \]

#### GSDMM model was applied on the lemmatized tweets. Based on running the above hyperparameter tuning on a smaller set of data, it was determined that the maximum number of topics we select should be five. Coherence measure were not created as experimenting with LDA showed that with more topics there was substantial overlap and no distinct separation of topics. Another observation was that the discrimination of Disney adventure ride versus the expedition occurs more cleanly and without overlap when around 1000 tweets are provided. Increasing this amount causes fuzziness, 

- This is based not only on the coherence scores but also on
  observations and deep look into the topics created as seen by the
  analysis below.

- For the number of iterations, convergence occurs at about 7 topics and
  in this case some of the topics do not have any documents in them or
  have documents in the single digit.

- For instance for 13 topics:Count of documents per topic : \[ 0 0 0 589
  166 18 0 0 3401 136 651 39 0\] Seven of the clusters contain all the
  documents.

- The first topic which is predominant lists Disney ride “Expedition
  Everest”

- The second topic is better restricted to Everest and Himalaya treks

- When 4 or more topics are introduced, then from the third topic, we
  tend to see an overlap of the above two topics and do not intuitively
  make much sense .

Alpha and Beta hyperparameters were also tuned with values from 0.01
through 0.1  
Npte that we cannot use Gensim’s dictionary with the words being
lemmatized using Spacy and so Coherence measure were not calculated,
instead the more reliable method of manually inspecting the topics was
used.

An overall look into the topics appear to broadly split the words into
Disney related and Mount Everest expedition related and so we will start
off by labeling the entire dataset based on five topics alone.  
  
Looking at 5 topic model, which appears to have a cleaner separation of
topic words:  
  
Cluster document counts for topic cluster 5 :**\[440, 397, 307, 2912,
944\]**  
For number of topics = 5 the top 10 words in the topics are  
**  
**- Topic 0 (440) - \['everest', 'expedition', 'adventure', 'base_camp',
'mount', 'nepal', 'trek', 'summit', 'info_aspire', 'amp', 'travel',
'world', 'adventure_dreamexplorediscover', 'everestbasecamp', 'snowdon',
'climber', 'mountain', 'team', 'high', 'explore', 'love',
'kilimanjaro_everestbasecamp', 'challenge', 'teamwork', 'let'\],  
  
- Topic 1 (397) \['everest', 'expedition', 'team_member',
'proceed_loading', 'platform_board', 'seat_immediately',
'pull_restraint', 'secure_gear', 'cargo_bag', 'great_trip', 'base_camp',
'mount', 'nepal', 'ada', 'pengen', 'reach_summit', 'southwest_face',
'face', 'dan', 'person', 'die', 'tahun', 'camp', 'lagi', 'yang'\],  
  
- Topic 2 (307) \['everest', 'expedition', 'mountain', 'base_camp',
'flight', '"', 'mount', 'ride', 'space', 'que', 'coaster', 'dinosaur',
'houston', 'tower_terror', 'animal_kingdom', 'flight_passage', '’s',
'river_journey', 'passage', 'star', '’', 'tour', 'avatar_flight',
'expédition', 'big_thunder'\],  
  
- Topic 3 (2912) \['everest', 'expedition', 'base_camp', 'trek', 'day',
'time', 'climb', '"', 'mount', 'nepal', 'like', 'ride', 'year', 'want',
'mountain', '’s', 'today', 'I\_’m', 'yeti', 'think', 'amp',
'ride_expedition', 'hike', 'people', 'good'\],  
  
- Topic 4 (944) \['everest', 'disneyworld', 'legend_forbidden',
'mountain', 'pass_expedition', 'lightning_lane', 'wdw_waltdisneyworld',
'distribution_new', 'start_animalkingdom', 'away_animalkingdom',
'expedition', 'mickey_mouse', 'run', 'snow_white', 'aquire',
'grapefruit_cake', 'sail_disneyworld', 'piglet', 'waffle',
'donald_duck', 'time', 'pineapple_dolewhip', 'spend_money',
'tiana_expedition', 'jasmine_expedition'\]  
  
  
The hyperparameters chosen therefore are  
  
K = 4  
alpha=0.1  
beta=0.5,

**Scatter Text**

Simply described, Scatter Text is a Word Cloud come alive with
interactivity and search capabilities and ability to drill into the
lemmatized tweets that served up the topic words. There is a limitation
that it allows for only two topics along the X and Y axis and so, after
picking the model with the number of topics that shows best demarcation
among the topics (this is performed manually) the topics are further
consolidated into Everest related and other topics called Entertainment
as a whole.

“Word clouds can be difficult to interpret. It is difficult to compare
the sizes of two nonhorizontally adjacent words, as well as the relative
color intensities of any two words. Longer words unintentionally appear
more important since they naturally occupy more space in the cloud.
Sizing of words can be a source of confusion when used to represent
precision, since a larger word may naturally be seen as more frequent”
(https://aclanthology.org/P17-4015.pdf)

To support ScatterText’s requirement to visualize the main topic under
discussion on one axis and counter topic(s) in another, the five topics
were further condensed into 2. Where the tweets clearly had Disney
hashtags, these were placed in the counter topic called Entertainment.
Further more,

Topic 0 and Topic 1 and Topic 3 have a higher frequency of everest
related words such as base camp, summit, secure gear, nepal, southwest
face, reach summit and hike  
  
Topic 2 and Topic 4 Disney and entertainment related with words such as
, 'animal_kingdom', 'flight_passage', 'donald_duck', 'time',
'pineapple_dolewhip', 'spend_money', 'tiana_expedition',
'jasmine_expedition'

**Insights gained**

<img src=".\/media/image21.jpeg" style="width:6.5in;height:3.05208in" />

**\##** \[Details about scattertext from Jason
Kessler\](*https://github.com/JasonKessler/Scattertext-PyData/blob/master/PyData-Scattertext-Part-1.ipynb*)  
  
**\***How is an association made between a word and a category?**\***  
Associated terms have a relatively high category-specific precision and
category-specific term frequency (i.e., % of terms in category are term)
and so take the harmonic mean of precision and frequency (both have to
be high)  
  
Reading from the scattertext graph:

The words “determination” and “abandon” feature high up to the left and
close to the Everest Frequency axis. The top left quandrant also
contains words such as challenging, and names of peaks such as
annapurna_circuit, and manslu. The bottom right is as far away from
expedition axis and contains words such as florida and swimming.
Clicking on each of these terms in the document reveals the tweets that
fed the classifier with the frequency of these terms.  
  
Words and their tweets that have been lemmatized using Spacy:  
**\`**determination**\`  
-** epitomise average new zealander modest ability good deal
determination like succeed sir edmund hillary  
**-** yunho know determination big mount everest push far  
  
**\`**challenge**\`  
-** enjoy beautiful everest region exciting challenging route
magnificent beauty wouldn like miss grab chance enjoy trek
nepaltourspackag everest base camp gokyo lake trek day  
**-** challenging thing world climb mount everest finish marathon hour
play das haus use shotgun vanguard  
**-** trek everest challenging rewarding  
**-** pakistani mountaineer shehroze kashif fazal ali nanga parbat duo
safely rappel technically challenging kinshofer wall civilization
congratulation  
**\`**gokyo_lake**\`  
-** enjoy beautiful everest region exciting challenging route
magnificent beauty wouldn like miss grab chance enjoy trek
nepaltourspackag everest base camp gokyo lake trek day  
**-** gokyo lake frozen stir nepal travel adventure explore trek everest
basecamp ebc everestbasecamp

**\[Note: Lemmatized tweets have been placed here\]  
  
  
**Top Everest words  
  
**-** nepal  
**-** mountain_conquer  
**-** quote_day  
**-** trek  
**-** summit  
**-** quote  
**-** climber  
**-** leadership  
**-** wander  
**-** peak  
**-** edmund_hillary  
**-** sherpa  
**-** heute  
**-** high_speed  
\`  
  
Top Entertainment words  
  
**-** home_run  
**-** mark_mcgwire  
**-** total_foot  
**-** record_set  
**-** season_travel  
**-** ride_expedition  
**-** animal_kingdom  
**-** lightning_lane  
**-** wdw_waltdisneyworld  
**-** pass_expedition  
**-** disneyworld  
**-** equip  
**-** ride  
**-** submerge_mile  
  
  
A quote by Edmund Hillary is one of the most repeated tweets:  
In lemmatized form it reads:  
**\>** mountain conquer sir edmund hillary quoteoftheday
mountainsdontfightback conqueryourfear overcome  
**\>** The original quote : It is not the mountain we conquer but
ourselves  
  
People tweet when concerned about a 'climber'  
**\>** chhang dawa sherpa today army helicopter saijd search flight
aerial reconnaissance hour maximum limit locate miss climber ali john
snorri juan pablo mohr  
**\>** corpse climber sherpas mount everest extreme weather prevent
removal preserve  
**\>** breakingnew official climber fear miss avalanche sweeps mount
everest  
  
  
Words more closely and clearly aligned to the Everest Frequency axis
(but are infrequent)  
**\>** leadership, leadership_courage, tenzing_norgay (Tenzing Norgay),
die_new, supplemental_oxygen. bucketlist, challenge_charity, cost  
  
This set of words describes the characteristics people are looking for
when going on the trek and to some extent shows motivation such as
challenge, charity or that it has been on their bucket list. The cost of
the expedition will be of concern with these tours and trek becoming
more expensive with popularity.  
  
Also close to this axis are words such as single_deadly fed by tweets
such as : (note that you can click on a word to reveal the tweets)  
**\>** avalanche kill single deadly accident mount everest  
**\>** avalanche kill single deadly accident mount everest cnn
cnnavalanche kill single deadly accident mount  
  
  
Words less tightly bound Everest Frequency axis but are more frequent to
the Everest topic (top left quadrant):  
**\>** ascent, training, nepal, china, trekking, sherpa,
mountain_conquer, guide, reach_summit, internet, tent, airport \`  
  
Having functional internet for close communication and for weather
details appears to be on the mind of people who tweet. Route locations
start from a country such as Nepal or China and political situation will
be closely monitored by those interested in an expedition. Getting to
mountain and to the closest airport is a point of discussion as well.  
**\>** high speed internet mount everest  
**\>** high point world cell service internet capability high peak mount
everest  
  
**\>** mile airport city mount everest base camp week trip china  
**\>** fly tenze hillary airport lukla nepal dangerous world gateway
everest base camp trek  
**\>** everest summit expedition kick tomorrow march departure place
henri coandă airport bucharest  
  
The Disney related words are closer along the entertainment axis along
with other entertainment associated words such as:  
lion_king, ride_expedition  
  
**\>** safari trip expedition everest rollercoaster watch festival lion
king eat rainforest cafe  
**\>** expedition everest times hour wait lion king rain pretty hard
outside  
**\>** watch lion king expedition everest  
**\>** ride expedition everest time row  
  
And for some reason the baseball legend MArk McGwire trends in these
tweets along with Mount Everest, perhaps an advertisement by an
organization  
**\>** mark mcgwire record set home run season_travel total_foot fly
mount everest

