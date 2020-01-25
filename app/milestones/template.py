def verify(data,milestone):
    '''
    Method used for verify the milestone. It is executed when /verifyMilestone is called.
    Parameters:
        Input:
            - Data: dictionary with all the attributes setted as args in the request, e.g. /verifyMilestone/?answer="Two"
            - Milestone: Object milestone where some interesting parameters like id or mode can be found.

        Output: IMPORTANT: It is mandatory to send what is required there
            - Answer: True or False. It is the actual verification of the response of the user. The system takes it for
                        loggin the information.
            - Points: Assing points to the user that completes the milestone.

        Additional data:
            - The support file that is uploaded through the platform can be taken with:
                file=os.getcwd()+"/app/milestones/files/"+milestone.mode+"_"+str(milestone.id)+"."+format
                    with format equals to the format of the wanted file


    '''

    format='csv' # Change wanted format

    file=os.getcwd()+"/app/milestones/files/"+milestone.mode+"_"+str(milestone.id)+"."+format

    if os.path.isfile(file):
        #If file exist, open it and read it
        file_content=open(file)

    result={
    "answer": True,
    "points": 900
    }
    return result

def load(milestone):

    '''
    Method used for load content of the milestone. It is executed before the milestone template is rendered.
    Parameters:
        Input:
            - Milestone: Object milestone where some interesting parameters like id or mode can be found.
            Check app/Models.py for further information.

        Output: IMPORTANT: It is mandatory to send what is required there
            - data: Dictionary that contains all the parameters that can be changed in the template.

        Additional data:
            - The support file that is uploaded through the platform can be recovered with:
                file=os.getcwd()+"/app/milestones/files/"+milestone.mode+"_"+str(milestone.id)+"."+format
                    with format equals to the format of the wanted file

    '''

    format='csv' # Change wanted format

    file=os.getcwd()+"/app/milestones/files/"+milestone.mode+"_"+str(milestone.id)+"."+format

    data = {
    'question': 'How much is 1+1?',
    'description': 'Provide an Integer result.'
    }

    return data
