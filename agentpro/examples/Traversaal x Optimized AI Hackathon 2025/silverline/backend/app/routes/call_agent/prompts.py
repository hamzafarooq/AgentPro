class Prompts:
    
    classify_call_prompt: str = """From the following call transcript, please extract the following key details:
    
1. **Spam Classification**: Determine whether the call is **SPAM**, **NOT_SPAM**, or **NOT_SURE**.
2. **Call Reason**: Provide a brief and clear summary explaining the reason for the call.
3. **Call Type**: Categorize the call into one of these categories: **MEDICAL_HEALTH**, **ENVIRONMENTAL**, **EMOTIONAL_DISTRESS**, **DAILY_LIVING**, **OTHER**, or **NOT_SURE**.

**Background**: The call transcript documents a conversation between an elderly person in need of help and an emergency helpline agent.

⚠️ **Important**: If there is not enough information to confidently determine one or more of these details, do not assume or hallucinate. In such cases, return `"NOT_SURE"` for that particular detail along with an appropriate explanation in the **reason** field.

Return the result strictly in the following JSON format based on the Pydantic schema below:

```python
class CallType(StrEnum):
    MEDICAL_HEALTH : str = "MEDICAL_HEALTH"
    ENVIRONMENTAL : str = "ENVIRONMENTAL"
    EMOTIONAL_DISTRESS : str = "EMOTIONAL_DISTRESS"
    DAILY_LIVING : str = "DAILY_LIVING"
    OTHER : str = "OTHER"
    NOT_SURE : str = "NOT_SURE"

class IsSpam(StrEnum):
    SPAM : str = "SPAM"
    NOT_SPAM : str = "NOT_SPAM"
    NOT_SURE : str = "NOT_SURE"

class CallClassification(BaseModel):
    is_spam: IsSpam
    reason: str
    type: CallType

The call transcript is:

{call_transcript}
"""

