from django.conf import settings
import dialogflow_v2 as dialogflow
import os

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.join(settings.BASE_DIR, 'chatbot.json'))

def dialogflow_call(session_id, text):
	session_client = dialogflow.SessionsClient() 
	session = session_client.session_path(
		settings.DIALOGFLOW_PROJECT_ID, 
		session_id
	)
	text_input = dialogflow.types.TextInput(
		text=text, 
		language_code='en'
	) 
	query_input = dialogflow.types.QueryInput(text=text_input)
	response = session_client.detect_intent(
		session=session, 
		query_input=query_input
	)

	return {
		'query_text': response.query_result.query_text,
		'display_name': response.query_result.intent.display_name,
		'confidence':response.query_result.intent_detection_confidence,
		'fulfillment_text': response.query_result.fulfillment_text
	}