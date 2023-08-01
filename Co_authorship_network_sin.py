

import matplotlib.pyplot as plt
import networkx as nx
import urllib3
from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import seaborn as sns
import pandas as pd

scholar = 'https://scholar.google.com/citations?user=x6fNSxcAAAAJ&hl=en'
nodes=100

def getGraph(seed, Nmax):
    urls = defaultdict(int)
    urls[seed]+=1
    newUrls = [seed]
    G = nx.DiGraph()

    def coAuthors(url):
        print(url)
        coUrls = []
        coNames = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        s = soup.body.findAll('a', {"tabindex": "-1"})
        egoName = soup.body.find('div', {"id": "gsc_prf_in"}).text
        print(egoName)
        print("******")
        if s:
            for i in s:
                if i.text=="Sort by citations" or i.text=="Sort by year" or i.text=="Sort by title":
                  continue
                coNames.append(i.text)
                #for network plot
                coUrls.append('http://scholar.google.nl'+ i['href'])
        for j in coUrls:
            urls[j] += 0
        for m in coNames:
            G.add_edge(egoName.split(',')[0], m.split(',')[0], weight = 1)
        return coUrls

    while newUrls:
        for k in urls.keys():
            # update url.values() first
            urls[k] += 1
        addUrls = []
        # get new-added authors, may have duplications.
        for i in newUrls:

            #coAuthors(i)
            coUrls = coAuthors(i)
            if coUrls:
                for j in coUrls:
                    addUrls.append(j)
        for m in set(addUrls):
            # get rid of the duplications
            urls[m] += 0
        newUrls = [k for k, v in urls.items() if v <= 1]
        # This is for updating the new coauthors and avoid the deadloop: a->b->a->......
        addUrls = []
        print(len(urls.keys()))
        if len(urls.keys()) > Nmax:
            print('more than '+str(Nmax)+' people now, break')
            break
        print(newUrls)
    return G

def getName(seed, Nmax):
    #urls = defaultdict(int)
    G = nx.DiGraph()
    response = requests.get(seed)
    soup = BeautifulSoup(response.content, "html.parser")
    egoName = soup.body.find('div', {"id": "gsc_prf_in"}).text
    print(egoName)
    return egoName

#get Name of the author
name = getName(scholar, nodes)

#get coauthor List
g = getGraph(scholar, nodes)

def plot_(g):
    plt.figure(figsize = (30, 30))
    pos = nx.spring_layout(g)
    nx.draw_networkx_labels(g, pos, font_color='k', font_size = 14)
    nx.draw(g, pos, node_size = 20, edge_color = 'grey', width = 0.4, arrows = True)
    #str1=name
    str2="'s Google Scholar Network"
    myTitle=str(name)+str2
    plt.title(myTitle, fontsize=40)
    #plt.xticks([])
    #plt.yticks([])
    plt.show()

plot_(g)

#create Important subnetwork
def page_Rank(G):
    print("Google Page Rank Algoritham\n")
    rank = nx.pagerank(G)
    for k,v in rank.items() :
        print("Page Rank Centrality :",k,'\t',v)

    r = [x for x in rank.values()]
    rsum = sum(r)
    rlen = len(r)
    rfac = rsum/rlen
    Gt = G.copy()

    for k, v in rank.items():
        if v < rfac:
            Gt.remove_node(k)
    return Gt

Gt = page_Rank(g)

plot_(Gt)

mylist=[]
degree =  g.degree()
for k,v in degree :
    print('Degree of Each Node :',k,'\t',v)
    mylist.append(v)

plt.figure(figsize = (8, 5))
plt.hist(mylist)
plt.title("Degree Distribution", fontsize = 15)
plt.show()

centality_value = []
centrality =  nx.degree_centrality(g)
for each in centrality.items():
    print('Degree Centrality: ', each[0], '\t', each[1])
    centality_value.append(each[1])

avg_centrality =  sum(centrality.values())/len(centrality)
print('Average Degree Centrality: ', avg_centrality)

#create dataframe
import pandas as pd
y=list(centrality.values())
x=list(centrality.keys())
data = {'keys':x,'values':y}
df1 = pd.DataFrame.from_dict(data)

sns.set_style('darkgrid')
a=sns.displot(df1)
a.set_axis_labels(x_var="Degree Centrality", y_var="No. of co-authors")

close = nx.closeness_centrality(g)
for each in close.items():
    print('Closeness Centrality: ', each[0], '\t', each[1])

avg_closeness =  sum(close.values())/len(close)
print('Average Closeness: ', avg_closeness)

y=list(close.values())
x=list(close.keys())
data = {'keys':x,'values':y}
df1 = pd.DataFrame.from_dict(data)

sns.set_style('darkgrid')
a=sns.displot(df1)
a.set_axis_labels(x_var="Closeness Centrality", y_var="No. of co-authors")

btwn = nx.betweenness_centrality(g, weight='weight')
for each in btwn.items():
    print('Betweeness Centrality: ', each[0], '\t', each[1])

avg_betweenness =  sum(btwn.values())/len(btwn)
print('Average Betweenness: ', avg_betweenness)

y=list(btwn.values())
x=list(btwn.keys())
data = {'keys':x,'values':y}
df1 = pd.DataFrame.from_dict(data)


sns.set_style('darkgrid')
a=sns.displot(df1)
a.set_axis_labels(x_var="Betweenness Centrality", y_var="No. of co-authors")

def plot2(g, strng):
  plt.figure(figsize=(35, 35))

  # 1. Create the graph
  # df=pd.read_csv("aaa.csv", encoding= 'unicode_escape')
  # g=nx.from_pandas_edgelist(df, source='author', target='coauthors')
  df=nx.to_pandas_edgelist(g)
  #print(df)
  # 2. Create a layout for our nodes
  layout = nx.spring_layout(g,iterations=50)

  # 3. Draw the parts we want
  nx.draw_networkx_edges(g, layout, edge_color='#AAAAAA')

  coauthor = [node for node in g.nodes() if node in df.target.unique()]
  size = [g.degree(node) * 80 for node in g.nodes() if node in df.target.unique()]
  nx.draw_networkx_nodes(g, layout, nodelist=coauthor, node_size=size, node_color='lightblue')

  people = [node for node in g.nodes() if node in df.source.unique()]
  nx.draw_networkx_nodes(g, layout, nodelist=people, node_size=100, node_color='#AAAAAA')

  high_degree_people = [node for node in g.nodes() if node in df.source.unique() and g.degree(node) > 1]
  nx.draw_networkx_nodes(g, layout, nodelist=high_degree_people, node_size=100, node_color='#fc8d62')

  coauthors_dict = dict(zip(coauthor, coauthor))
  nx.draw_networkx_labels(g, layout, labels=coauthors_dict)

  plt.axis('off')

  plt.title("Justin Wolfer's Google Scholar Network", fontsize=30)
  # 4. Tell matplotlib to show it
  plt.savefig(strng)
  plt.show()
plot2(g, "network.png")

plot2(Gt, "impnetwork.png")