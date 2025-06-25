import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

FASTAPI_ENDPOINT = "http://localhost:8000/query/"

class ActionRespondPdfContent(Action):
    def name(self):
        return "action_respond_pdf_content"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: dict):
        query = tracker.latest_message.get("text")

        if not query:
            dispatcher.utter_message(text="I didn't understand your question.")
            return []

        try:
            response = requests.post(FASTAPI_ENDPOINT, data={"query": query})
            result = response.json()

            if response.status_code != 200 or "error" in result:
                dispatcher.utter_message(text="⚠️ Error fetching response.")
                return []

            dispatcher.utter_message(text=result["response"])
            for url in result.get("images", []):
                dispatcher.utter_message(image=url)

        except Exception as e:
            dispatcher.utter_message(text=f"Error calling backend: {e}")

        return []
