from typing import TypedDict, List, Optional, Any

class AgentState(TypedDict):
    question: str
    messages: List[Any]
    sql_query: Optional[str]
    sql_result: Optional[str]
    web_results: Optional[str]
    iterations: int
