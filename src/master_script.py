import os
import parse_text
import sop_topics_situation_kmeans_tfidf
import sop_topics_type_kmeans_tfidf
import type_flowchart
import situ_flowchart

# Create empty default directory
try:
    os.makedirs("data/")
    print("Directory created at 'data/'")
except:
    print("data Directory already exists in root dir. Proceeding....")
try:
    os.makedirs("data/interim/")
except:
    print("interim Directory already exists in root/data. Proceeding....")
try:
    os.makedirs("data/sop_jsons/")  
except:
    print("sop_jsons Directory already exists in root/data. Proceeding....") 
try:
    os.makedirs("img/")
except:
    print("img Directory already exists in root dir. Proceeding....") 
try:
    os.makedirs("img/flowcharts/")
except:
    print("img Directory already exists in root dir. Proceeding....") 


print('Start parsing SOP documents')
parse_text.main()
print('Parsing completed...')
assert len(os.listdir("data/interim/")) >= 5

print('Start cross-type clustering')
sop_topics_type_kmeans_tfidf.main()
print('Cross-type clustering completed...')

print('Start cross-situation clustering')
sop_topics_situation_kmeans_tfidf.main()
print('Cross-situation clustering completed...')

print('Start generating cross-type flowcharts')
type_flowchart.main()
print('Cross-type flowcharts completed...')

print('Start generating cross-situation flowcharts')
situ_flowchart.main()
print('Cross-situation flowcharts completed...')

print('Master script ends here.')
