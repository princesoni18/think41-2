

import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.controllers.conversation_controller import get_conversation
from app.tools import db_tools
import re

# Set up logger
logger = logging.getLogger("think41_chatbot")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)





# Load environment variables from .env file
load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

class Think41ChatBot:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_GEMINI_API_KEY,
            temperature=0.2,
        )
        self.tools = {
            "query_order_by_id": {
                "pattern": r"(?:order|status).*?(?:id|ID)[\s:]*([A-Za-z0-9-]+)",
                "description": "Query order details by order ID",
                "function": db_tools.query_orders_by_order_id
            },
            "query_orders_by_user_id": {
                "pattern": r"orders?.*?user[\s_]?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query all orders by user ID",
                "function": db_tools.query_orders_by_user_id
            },
            "query_product_by_id": {
                "pattern": r"product.*?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query product details by product ID",
                "function": db_tools.query_product_by_id
            },
            "query_product_by_name": {
                "pattern": r"product.*?name[\s:]*['\"]?([^'\"]+)['\"]?",
                "description": "Query product details by product name",
                "function": db_tools.query_products_by_name
            },
            "query_user_by_id": {
                "pattern": r"user.*?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query user details by user ID",
                "function": db_tools.query_user_by_id
            },
            "query_user_by_email": {
                "pattern": r"user.*?email[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                "description": "Query user details by email address",
                "function": db_tools.query_user_by_email
            },
            "query_inventory_by_product_id": {
                "pattern": r"(?:inventory|stock).*?product[\s_]?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query inventory by product ID",
                "function": db_tools.query_inventory_by_product_id
            },
            "query_inventory_item_by_id": {
                "pattern": r"inventory.*?item.*?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query inventory item by item ID",
                "function": db_tools.query_inventory_item_by_id
            },
            "query_distribution_center": {
                "pattern": r"(?:distribution|dc).*?(?:center|id)[\s:]*([A-Za-z0-9-]+)",
                "description": "Query distribution center details",
                "function": db_tools.query_distribution_center_by_id
            },
            "query_order_items": {
                "pattern": r"order.*?items.*?order[\s_]?id[\s:]*([A-Za-z0-9-]+).*?user[\s_]?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query order items by order ID and user ID",
                "function": lambda oid, uid: db_tools.query_order_items_by_order_and_user(oid, uid)
            },
            "query_order_item_by_id": {
                "pattern": r"order.*?item.*?id[\s:]*([A-Za-z0-9-]+)",
                "description": "Query order item by item ID",
                "function": db_tools.query_order_item_by_id
            }
        }

    def get_system_instruction(self) -> str:
        return (
            """
You are Think41's AI customer service assistant for our e-commerce clothing platform.

ALWAYS analyze the conversation history to find any information the user has already provided. NEVER ask for information that is already present in the conversation context.

When you have enough information to answer a user's request using a database tool, respond IMMEDIATELY with:
TOOL_CALL: [exact_tool_name] [parameters_separated_by_spaces]

TOOL_CALL format examples:
- TOOL_CALL: query_order_by_id 12345
- TOOL_CALL: query_product_by_name Nike Air Max
- TOOL_CALL: query_user_by_email john@email.com
- TOOL_CALL: query_order_items 12345 67890

Available tool names (use these exactly):
query_order_by_id
query_product_by_name
query_user_by_email
query_inventory_by_product_id
query_distribution_center
query_order_items

If you do not have enough information, ask the user for only the missing details. If you cannot find specific information, suggest alternative ways the user can get help.

Be friendly, helpful, and always refer to the company as Think41.
"""
        )

    def get_conversation_history(self, user_id, conversation_id):
        history = ""
        if user_id and conversation_id:
            conv = get_conversation(user_id, conversation_id)
            if conv and "messages" in conv:
                for msg in conv["messages"]:
                    history += f"{msg['sender'].capitalize()}: {msg['text']}\n"
        return history

    def parse_tool_call(self, response_text):
        # Improved regex and parameter handling
        match = re.search(r"TOOL_CALL:\s*(\w+)(?:\s+(.+))?", response_text)
        if not match:
            logger.warning(f"Malformed TOOL_CALL: {response_text}")
            return None, []
        tool_name = match.group(1)
        params_str = match.group(2) or ""
        # Special handling for email, product name, and order items
        if tool_name == "query_user_by_email":
            email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", params_str)
            params = [email_match.group(1)] if email_match else []
        elif tool_name == "query_product_by_name":
            # Product name may contain spaces, take the whole string
            params = [params_str.strip()] if params_str else []
        elif tool_name == "query_order_items":
            # Expect exactly 2 params
            params = params_str.strip().split()
            if len(params) != 2:
                logger.warning(f"TOOL_CALL for order_items expects 2 params, got: {params}")
        else:
            params = params_str.strip().split() if params_str else []
        logger.info(f"Parsed TOOL_CALL: {tool_name} with params {params}")
        return tool_name, params

    def extract_info_from_context(self, message, user_id, conversation_id):
        """
        Analyze conversation history and current message to extract actionable info for tool calls.
        Returns: (tool_name, params) or (None, [])
        """
        history = self.get_conversation_history(user_id, conversation_id)
        context = history + f"User: {message}\n"
        # Order ID (must be at least 3 alphanumeric chars, not common words)
        order_id_match = re.search(r"order[\s\w]*id[\s:]*([A-Za-z0-9-]{3,})\b", context, re.IGNORECASE)
        if order_id_match:
            order_id = order_id_match.group(1)
            # Avoid matching common words like 'is', 'it', etc.
            if order_id.lower() not in {"is", "it", "the", "a", "an", "status", "order", "id"}:
                logger.info(f"Order ID found in context: {order_id}")
                return "query_order_by_id", [order_id]
        # Product name (must be at least 3 chars, not common words)
        product_name_match = re.search(r"product[\s\w]*name[\s:]*['\"]?([^'\"\n]{3,})['\"]?", context, re.IGNORECASE)
        if product_name_match:
            pname = product_name_match.group(1).strip()
            if pname.lower() not in {"is", "it", "the", "a", "an", "name", "product"}:
                logger.info(f"Product name found in context: {pname}")
                return "query_product_by_name", [pname]
        # Email
        email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", context)
        if email_match:
            logger.info(f"Email found in context: {email_match.group(1)}")
            return "query_user_by_email", [email_match.group(1)]
        # Order items (order_id and user_id, both must be at least 3 chars, not common words)
        oi_order_id = re.search(r"order[\s\w]*id[\s:]*([A-Za-z0-9-]{3,})\b", context, re.IGNORECASE)
        oi_user_id = re.search(r"user[\s\w]*id[\s:]*([A-Za-z0-9-]{3,})\b", context, re.IGNORECASE)
        if oi_order_id and oi_user_id:
            oid = oi_order_id.group(1)
            uid = oi_user_id.group(1)
            if oid.lower() not in {"is", "it", "the", "a", "an", "status", "order", "id"} and uid.lower() not in {"is", "it", "the", "a", "an", "status", "order", "id", "user"}:
                logger.info(f"Order items context found: order_id={oid}, user_id={uid}")
                return "query_order_items", [oid, uid]
        # Inventory by product_id (must be at least 3 chars, not common words)
        product_id_match = re.search(r"product[\s_]?id[\s:]*([A-Za-z0-9-]{3,})\b", context, re.IGNORECASE)
        if product_id_match:
            pid = product_id_match.group(1)
            if pid.lower() not in {"is", "it", "the", "a", "an", "id", "product"}:
                logger.info(f"Product ID for inventory found in context: {pid}")
                return "query_inventory_by_product_id", [pid]
        # Distribution center by id (must be at least 3 chars, not common words)
        dc_id_match = re.search(r"distribution[\s\w]*center[\s\w]*id[\s:]*([A-Za-z0-9-]{3,})\b", context, re.IGNORECASE)
        if dc_id_match:
            dcid = dc_id_match.group(1)
            if dcid.lower() not in {"is", "it", "the", "a", "an", "id", "center", "distribution"}:
                logger.info(f"Distribution center ID found in context: {dcid}")
                return "query_distribution_center", [dcid]
        return None, []

    def execute_extracted_info(self, tool_name, params, user_id=None, conversation_id=None):
        logger.info(f"Executing tool from context: {tool_name} with params {params}")
        return self.handle_tool_call(tool_name, params, user_id=user_id, conversation_id=conversation_id)

    def handle_tool_call(self, tool_name, params, user_id=None, conversation_id=None):
        tool = self.tools.get(tool_name)
        if not tool:
            logger.warning(f"Tool {tool_name} not found.")
            return f"Sorry, I don't have a tool named '{tool_name}'."
        try:
            if tool_name == "query_order_items" and len(params) == 2:
                result = tool["function"](params[0], params[1])
            elif len(params) == 1:
                result = tool["function"](params[0])
            else:
                return f"Invalid parameters for tool '{tool_name}'."
            logger.info(f"Tool {tool_name} called with params {params}: {result}")
            if not result:
                return f"No data found for {tool_name} with parameters {params}."
            # Send raw info to LLM for conversational summary
            return self.llm_summarize_tool_result(tool_name, result, params, user_id, conversation_id)
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"Error calling tool {tool_name}: {e}"

    def llm_summarize_tool_result(self, tool_name, result, params, user_id=None, conversation_id=None):
        # Compose a prompt for the LLM to summarize the tool result in a conversational way
        system_instruction = (
            "You are Think41's AI customer service assistant. "
            "Given the following database information, explain it to the user in a friendly, clear, and helpful way. "
            "Do not show raw JSON or technical details. Use natural language and only the relevant facts."
        )
        history = self.get_conversation_history(user_id, conversation_id)
        prompt = (
            f"{system_instruction}\n"
            f"Conversation so far:\n{history}"
            f"\nDatabase info: {result}\n"
            f"User: Please explain the above info."
        )
        logger.info(f"Prompt sent to Gemini for summarization: {prompt}")
        response = self.llm.invoke(prompt)
        response_text = str(response.content)
        logger.info(f"LLM summary response: {response_text}")
        return response_text

    def format_tool_result(self, tool_name, result, params):
        # Format each tool's result for user-friendly output
        if tool_name == "query_order_by_id":
            return f"Order {params[0]} status: {result.get('status', 'Unknown')}."
        elif tool_name == "query_product_by_name":
            return (
                f"Product: {result.get('name', 'N/A')}\n"
                f"Brand: {result.get('brand', 'N/A')}\n"
                f"Category: {result.get('category', 'N/A')}\n"
                f"Department: {result.get('department', 'N/A')}\n"
                f"Retail Price: ${result.get('retail_price', 'N/A')}\n"
                f"Cost: ${result.get('cost', 'N/A')}\n"
                f"SKU: {result.get('sku', 'N/A')}\n"
                f"Distribution Center ID: {result.get('distribution_center_id', 'N/A')}"
            )
        elif tool_name == "query_user_by_email":
            return (
                f"User: {result.get('first_name', '')} {result.get('last_name', '')}\n"
                f"Email: {result.get('email', 'N/A')}\n"
                f"Age: {result.get('age', 'N/A')}\n"
                f"Gender: {result.get('gender', 'N/A')}\n"
                f"Location: {result.get('city', 'N/A')}, {result.get('state', 'N/A')}, {result.get('country', 'N/A')}"
            )
        elif tool_name == "query_inventory_by_product_id":
            return (
                f"Inventory Item ID: {result.get('id', 'N/A')}\n"
                f"Product ID: {result.get('product_id', 'N/A')}\n"
                f"Cost: ${result.get('cost', 'N/A')}\n"
                f"Created At: {result.get('created_at', 'N/A')}\n"
                f"Sold At: {result.get('sold_at', 'N/A')}"
            )
        elif tool_name == "query_distribution_center":
            return (
                f"Distribution Center: {result.get('name', 'N/A')}\n"
                f"ID: {result.get('id', 'N/A')}\n"
                f"Latitude: {result.get('latitude', 'N/A')}\n"
                f"Longitude: {result.get('longitude', 'N/A')}"
            )
        elif tool_name == "query_order_items":
            if isinstance(result, list):
                if not result:
                    return f"No order items found for order_id {params[0]} and user_id {params[1]}."
                lines = [
                    f"Order Item ID: {item.get('id', 'N/A')}, Product ID: {item.get('product_id', 'N/A')}, Status: {item.get('status', 'N/A')}"
                    for item in result
                ]
                return "Order Items:\n" + "\n".join(lines)
            else:
                return str(result)
        else:
            # Default: pretty print dict
            return "Result: " + ", ".join(f"{k}: {v}" for k, v in result.items() if k != '_id')

    def get_response(self, message, user_id=None, conversation_id=None):
        try:
            # 1. Try to extract actionable info from context first
            tool_name, params = self.extract_info_from_context(message, user_id, conversation_id)
            if tool_name and params:
                logger.info(f"Context-aware tool execution: {tool_name} {params}")
                return self.execute_extracted_info(tool_name, params, user_id=user_id, conversation_id=conversation_id)

            # 2. If not enough info, send to LLM
            system_instruction = self.get_system_instruction()
            history = self.get_conversation_history(user_id, conversation_id)
            prompt = f"{system_instruction}\nConversation so far:\n{history}\nUser: {message}"
            logger.info(f"Prompt sent to Gemini: {prompt}")
            response = self.llm.invoke(prompt)
            response_text = str(response.content)
            logger.info(f"Gemini response: {response_text}")

            if "TOOL_CALL" in response_text:
                logger.info("TOOL_CALL detected in Gemini response. Attempting to parse and call the appropriate tool.")
                tool_name, params = self.parse_tool_call(response_text)
                if tool_name and params:
                    return self.handle_tool_call(tool_name, params, user_id=user_id, conversation_id=conversation_id)
                else:
                    logger.warning(f"TOOL_CALL found but could not parse tool or parameters: {response_text}")
                    return "Sorry, I could not understand the tool call. Please rephrase your request."

            logger.info(f"Returning Gemini response to user: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"Error in Think41ChatBot.get_response: {str(e)}")
            return f"Error: {str(e)}"
