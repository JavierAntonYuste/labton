import os, csv, codecs

def verify(data,milestone):
    format='csv' # Change wanted format
    email=data["user_email"][0]
    answer=data["answer"][0]

    result={}
    result["points"]=900
    result["answer"]=False

    file=os.getcwd()+"/app/milestones/files/"+milestone.mode+"_"+str(milestone.id)+"."+format

    if os.path.isfile(file):
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', dialect=csv.excel)

            read_file=[]
            for x in csv_reader:
                if x[0]== email:
                    if str(x[1])==str(answer):
                        result["answer"]=True
                    else:
                        result["answer"]=False
    else:
        print('File not exists')

    return result

def load(milestone):

    data = {
    "title": "Code question",
    "description": "Introduce your code below and check if it is correct!",
    "question": "Code"
    }
    return data
