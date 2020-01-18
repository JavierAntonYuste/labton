import os, csv

def verify(data,milestone):
    format='csv' # Change wanted format

    result={}
    result["points"]=0
    result["answer"]=True


    file=os.getcwd()+"/app/milestones/files/"+milestone.mode+"_"+str(milestone.id)+"."+format


    if os.path.isfile(file):
        with open(file,'a') as f:
            writer = csv.writer(f)
            writer.writerow([data["rating"][0],data["comment"][0]])

    else:
        print('File not exists')

    return result

def load(milestone):

    data = {
    "title": "Feedback",
    "description": "Write your feedback for your professor.",
    "text1": "Rating",
    "text2": "Comment"
    }
    return data
