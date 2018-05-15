import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import uuid
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


        

# --- Helper fuctions from aws lex documentation ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }



def confirm_intent(session_attributes, intent_name, slots, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message,
            'responseCard': response_card
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_response_card(title, options):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    if options is not None:
        buttons = []
        for i in range(min(5, len(options))):
            buttons.append(options[i])

    return {
        'contentType': 'application/vnd.amazonaws.card.generic',
        'version': 1,
        'genericAttachments': [{
            'title': title,
        
            'buttons': buttons
        }]
    }
# --- My functions ---


def safe_int(n):
    
    if n is not None:
        return int(n)
    return n


def try_ex(func):
     try:
        return func()
     except KeyError:
        return None


# used by intro intent

def intro(intent_request):
    session_attributes=None
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hey, this bot can do the following operations for you :\n\n1. It can give you some reference materials to enhance your skills.\n To get these information just type : "enhance my {topic} skills" or "{topic} tutorials" ,etc\n\n2. This bot can also test your skills by allowing you to give some tests.\n For giving test write : "test {topic}"\nIt also emails you your test score.\n\n3. It can also get you, your previious test score.\n For that write : "Show me my previous score"\n\n4. This bot can also show you some latest Tech news \n For that just write : "news"' 
      
        }
    )

# used by news intent

def news(intent_request):
    session_attributes= None
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You can get the lastest tech news from the following sites :\n1.https://www.techgig.com/tech-news/technology\n2.https://techcrunch.com/\n3.https://www.digit.in/technology-news/'
        }
        )

# used by cpp_tut  intent


def cpp_tut(intent_request):
    session_attributes= None
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You can learn more about cpp from the following links provided :\n1. You can also buy or audit a cpp course from :\nhttps://www.coursera.org/\n2. For Youtube video tutorials :\nhttps://www.youtube.com/watch?v=Gbzu759QIZQ&list=PLiOa6ike4WAEnWjWsLN6FDOApS9ED6x7v'
        }
        )
        
# used by java_tut intent

def java_tut(intent_request):
    session_attributes= None
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You can learn more about java from the following links provided :\n1. You can also buy or audit a java course from :\nhttps://www.coursera.org/\n2. For java tutorial on youtube :\n https://www.youtube.com/watch?v=r59xYe3Vyks&list=PLS1QulWo1RIbfTjQvTdj8Y6yyq4R7g-Al'
        }
        )
        
# used by python_tut intent

def python_tut(intent_request):
    session_attributes= None
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You can learn more about python from the following links provided :\n1. For Official documentation of python you can go to :\nhttps://docs.python.org/3/tutorial/index.html\n2. You can also buy or audit a python course from :\nhttps://www.coursera.org/\n3. For Youtube video tutorials :\nhttps://www.youtube.com/watch?v=HBxCHonP6Ro&list=PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_'
        }
        )
    
# used by java intent    
def java(intent_request):
    dynamo = boto3.resource('dynamodb')
    
    table = dynamo.Table('test_score')
    recordId = str(uuid.uuid4())
    name = try_ex(lambda: intent_request['currentIntent']['slots']['name'])
   
    email = try_ex(lambda: intent_request['currentIntent']['slots']['eid'])
    q1= try_ex(lambda: intent_request['currentIntent']['slots']['qu_a'])
    q2= try_ex(lambda: intent_request['currentIntent']['slots']['qu_b'])
    q3= try_ex(lambda: intent_request['currentIntent']['slots']['qu_c'])
    q4= try_ex(lambda: intent_request['currentIntent']['slots']['qu_d'])
    q5= try_ex(lambda: intent_request['currentIntent']['slots']['qu_e'])
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    reservation = json.dumps({
        'ReservationType': 'JAVA',
        'name': name,
        
        'email': email
        
    })
    
# for checking the answers

    session_attributes['currentReservation'] = reservation
    score=0
    if q1=='a':
        score=score+1
    if q2=='c':
        score=score+1
    if q3=='a':
        score=score+1
    if q4=='d':
        score=score+1
    if q5=='c':
        score=score+1    
# for putting data to dynamodb table

    DynamoDict = {
        'id': recordId,
        'topic': 'Java', 
        'name': name, 
        'email': email,
        'score': score
        
        
        }

    table.put_item(Item=DynamoDict)    

#for sending the emails through the use of aws ses service

    ses = boto3.client('ses')

    email_from = 'bhushansainidss.1@gmail.com'
    email_to = '{}'.format(email)
    email_cc = 'email'
    emaiL_subject = 'Subject'
    email_body = 'Body'
    pr=' Hey {},\nThanks for taking the Java skills test. Your test score is {} out of 5.\nYour percentage is {}.\n\n Have a great day, Visit Again.'.format(name,score,(score*100)/5)
                
    response = ses.send_email(
        Source = email_from,
        Destination={
            'ToAddresses': [
                email_to,
            ]
            
        },
        Message={
            'Subject': {
                'Data': 'SCORECARD FOR YOUR TEST'
            },
            'Body': {
                'Text': {
                    'Data': pr
                    
                }
            }
        }
    )
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks for taking the test. Your Score is {} out of 5. You got {} percentage and your unique test id is : {}.'.format(score,(score*100)/5,recordId)
                      
        }
    )            

# used by cpp intent

def cpp(intent_request):
    dynamo = boto3.resource('dynamodb')
    
    table = dynamo.Table('test_score')
    recordId = str(uuid.uuid4())
    name = try_ex(lambda: intent_request['currentIntent']['slots']['name'])
    
    email = try_ex(lambda: intent_request['currentIntent']['slots']['email'])
    q1= try_ex(lambda: intent_request['currentIntent']['slots']['que_a'])
    q2= try_ex(lambda: intent_request['currentIntent']['slots']['que_b'])
    q3= try_ex(lambda: intent_request['currentIntent']['slots']['que_c'])
    q4= try_ex(lambda: intent_request['currentIntent']['slots']['que_d'])
    q5= try_ex(lambda: intent_request['currentIntent']['slots']['que_e'])
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    reservation = json.dumps({
        'ReservationType': 'Cpp',
        'name': name,
        
        'email': email
        
    })
# for checking the answers

    session_attributes['currentReservation'] = reservation
    score=0
    if q1=='c':
        score=score+1
    if q2=='c':
        score=score+1
    if q3=='b':
        score=score+1
    if q4=='a':
        score=score+1
    if q5=='b':
        score=score+1    
        
#for putting data to dynamodb database

    DynamoDict = {
        'id': recordId,
        'topic': 'Cpp', 
        'name': name, 
        'email': email,
        'score': score
        
        
        }

    table.put_item(Item=DynamoDict)       
# for sending the emails using aws ses service 

    ses = boto3.client('ses')

    email_from = 'bhushansainidss.1@gmail.com'
    email_to = '{}'.format(email)
    email_cc = 'email'
    emaiL_subject = 'Subject'
    email_body = 'Body'
    pr=' Hey {},\nThanks for taking the Cpp skills test. Your test score is {} out of 5.\nYour percentage is {}.\n\n Have a great day, Visit Again.'.format(name,score,(score*100)/5)
                
    response = ses.send_email(
        Source = email_from,
        Destination={
            'ToAddresses': [
                email_to,
            ]
            
        },
        Message={
            'Subject': {
                'Data': 'SCORECARD FOR YOUR TEST'
            },
            'Body': {
                'Text': {
                    'Data': pr
                    
                }
            }
        }
    )
    
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks for taking the test. Your Score is {} out of 5. You got {} percentage and your unique test id is : {}.'.format(score,(score*100)/5,recordId)
                      
        }
    )            
               
# used by admin intent for retreiving the data from database

def admin(intent_request):
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('test_score')
    
    iid = try_ex(lambda: intent_request['currentIntent']['slots']['id'])
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
#making a get request
    try:
        response = table.get_item(
            Key={
                'id': iid
            
            }
            )
        topic=response['Item']['topic']
        name=response['Item']['name']
        score=response['Item']['score']
        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Hey {}, previously you took a {} test and you got {} marks out of 5.'.format(name,topic,score)
                
                      
            }
        )    
        
    except:
         
    
        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'You entered a wrong order id.'
                
                      
            }
        )    
   

    

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'Intro':
        return intro(intent_request)
    elif intent_name == 'java':
        return java(intent_request)
    elif intent_name == 'cpp':
        return cpp(intent_request)
    elif intent_name == 'Admin':
        return admin(intent_request)
    elif intent_name ==  'news':
        return news(intent_request)
    elif intent_name ==  'cpp_tut':
        return cpp_tut(intent_request)
    elif intent_name ==  'java_tut':
        return java_tut(intent_request)
    elif intent_name ==  'python_tut':
        return python_tut(intent_request)    
    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    intent_name = event['currentIntent']['name']
       
    return dispatch(event)

