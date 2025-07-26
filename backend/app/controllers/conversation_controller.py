from datetime import datetime
from app.services.database import db
from app.schemas.conversation_schema import Message
from bson import ObjectId


def save_message_to_conversation(user_id: str, conversation_id: str, sender: str, text: str):
    message = Message(sender=sender, text=text, timestamp=datetime.utcnow()).dict()
    user_doc = db.chats.find_one({"user_id": user_id})
    if not user_doc:
        # Create user doc with first conversation
        db.chats.insert_one({
            "user_id": user_id,
            "conversations": {
                conversation_id: {
                    "messages": [message],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        })
    else:
        # Upsert conversation in user's conversations
        update_query = {"user_id": user_id}
        update_op = {
            f"$push": {f"conversations.{conversation_id}.messages": message},
            f"$set": {f"conversations.{conversation_id}.updated_at": datetime.utcnow()},
            f"$setOnInsert": {f"conversations.{conversation_id}.created_at": datetime.utcnow()}
        }
        db.chats.update_one(update_query, update_op, upsert=True)

def get_conversation(user_id: str, conversation_id: str):
    user_doc = db.chats.find_one({"user_id": user_id})
    if user_doc and "conversations" in user_doc and conversation_id in user_doc["conversations"]:
        return user_doc["conversations"][conversation_id]
    return None
